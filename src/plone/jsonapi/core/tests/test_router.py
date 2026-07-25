# -*- coding: utf-8 -*-

"""Unit tests for the Router.

These exercise the router in isolation (no Plone layer needed): the
adapter binding derives host + scheme from the thread-local request, so
they use a fake request set via zope.globalrequest.
"""

import threading
import unittest2 as unittest

from plone.jsonapi.core.browser.exceptions import MethodNotAllowedError
from plone.jsonapi.core.browser.exceptions import NotFoundError
from plone.jsonapi.core.browser.router import Router
from zope.globalrequest import clearRequest
from zope.globalrequest import setRequest


class FakeRequest(object):
    """Minimal request stub for adapter binding + resolution."""

    def __init__(self, actual_url="http://nohost/plone/@@API", method="GET"):
        self._actual_url = actual_url
        self.environ = {"REQUEST_METHOD": method}

    def get(self, key, default=None):
        if key == "ACTUAL_URL":
            return self._actual_url
        return default


def make_router():
    router = Router()
    # Register a couple of rules directly (bypassing the IRouteProvider
    # machinery, which needs the component registry).
    router.add_url_rule(
        "/things", endpoint="things",
        view_func=lambda context, request: {"ok": True},
        options={"methods": ["GET"]})
    router.add_url_rule(
        "/things/<string:id>", endpoint="thing_update",
        view_func=lambda context, request, id: {"id": id},
        options={"methods": ["PATCH"]})
    return router


class TestAdapterIsRequestDerived(unittest.TestCase):
    """#1/#2: host and scheme come from the current request, not from
    state cached on the shared router singleton."""

    def tearDown(self):
        clearRequest()

    def test_host_from_current_request(self):
        router = make_router()
        setRequest(FakeRequest("http://a.example/plone/@@API"))
        self.assertEqual(router.get_adapter().server_name, "a.example")
        # A different request must yield a different host from the same
        # (singleton) router -- proving nothing is cached on self.
        setRequest(FakeRequest("http://b.example/plone/@@API"))
        self.assertEqual(router.get_adapter().server_name, "b.example")

    def test_scheme_from_current_request(self):
        router = make_router()
        setRequest(FakeRequest("https://secure.example/plone/@@API"))
        self.assertEqual(router.get_adapter().url_scheme, "https")
        setRequest(FakeRequest("http://plain.example/plone/@@API"))
        self.assertEqual(router.get_adapter().url_scheme, "http")

    def test_adapter_is_thread_local(self):
        # Two threads binding different hosts concurrently must not see
        # each other's host. The previous implementation stored
        # http_host on the singleton, so this could race.
        router = make_router()
        results = {}

        # Manual two-thread barrier (threading.Barrier is Python 3 only):
        # both threads set their request before either binds the adapter,
        # maximising the chance of a cross-thread clobber if the host were
        # stored on the shared router.
        lock = threading.Lock()
        arrived = [0]
        ready = threading.Event()

        def worker(host):
            setRequest(FakeRequest("http://%s/plone/@@API" % host))
            try:
                with lock:
                    arrived[0] += 1
                    if arrived[0] == 2:
                        ready.set()
                ready.wait(timeout=5)
                results[host] = router.get_adapter().server_name
            finally:
                clearRequest()

        t1 = threading.Thread(target=worker, args=("a.example",))
        t2 = threading.Thread(target=worker, args=("b.example",))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(results["a.example"], "a.example")
        self.assertEqual(results["b.example"], "b.example")


class TestResolve(unittest.TestCase):
    """#3: resolve() returns None on no-match (so callers can try the
    next router) and raises MethodNotAllowedError on a wrong method."""

    def tearDown(self):
        clearRequest()

    def test_resolve_returns_endpoint_and_values(self):
        router = make_router()
        req = FakeRequest("http://nohost/plone/@@API", method="GET")
        setRequest(req)
        endpoint, values = router.resolve(req, "/things")
        self.assertEqual(endpoint, "things")
        self.assertEqual(values, {})

    def test_resolve_returns_none_on_no_match(self):
        router = make_router()
        req = FakeRequest("http://nohost/plone/@@API", method="GET")
        setRequest(req)
        self.assertIsNone(router.resolve(req, "/does-not-exist"))

    def test_resolve_raises_method_not_allowed(self):
        router = make_router()
        req = FakeRequest("http://nohost/plone/@@API", method="DELETE")
        setRequest(req)
        # /things exists for GET, not DELETE.
        self.assertRaises(
            MethodNotAllowedError, router.resolve, req, "/things")

    def test_resolve_captures_path_values(self):
        router = make_router()
        req = FakeRequest("http://nohost/plone/@@API", method="PATCH")
        setRequest(req)
        endpoint, values = router.resolve(req, "/things/abc")
        self.assertEqual(endpoint, "thing_update")
        self.assertEqual(values, {"id": "abc"})


class TestMatchBackwardCompat(unittest.TestCase):
    """match() keeps its raising contract for existing callers."""

    def tearDown(self):
        clearRequest()

    def test_match_raises_not_found(self):
        router = make_router()
        req = FakeRequest("http://nohost/plone/@@API", method="GET")
        setRequest(req)
        self.assertRaises(
            NotFoundError, router.match, None, req, "/nope")

    def test_match_returns_tuple_on_hit(self):
        router = make_router()
        req = FakeRequest("http://nohost/plone/@@API", method="GET")
        setRequest(req)
        endpoint, values = router.match(None, req, "/things")
        self.assertEqual(endpoint, "things")

    def test_call_executes_view(self):
        router = make_router()
        req = FakeRequest("http://nohost/plone/@@API", method="PATCH")
        setRequest(req)
        result = router(None, req, "/things/xyz")
        self.assertEqual(result, {"id": "xyz"})


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdapterIsRequestDerived))
    suite.addTest(makeSuite(TestResolve))
    suite.addTest(makeSuite(TestMatchBackwardCompat))
    return suite
