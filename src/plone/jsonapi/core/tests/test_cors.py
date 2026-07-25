# -*- coding: utf-8 -*-

"""Unit tests for the CORS helpers.

Exercises the header-writing helper and the decorator in isolation
using fake request/response objects, so the tests don't need the
Plone fixture.
"""

import unittest2 as unittest

from plone.jsonapi.core.browser.cors import add_cors_headers
from plone.jsonapi.core.browser.cors import cors


class FakeResponse(object):
    def __init__(self):
        self.headers = {}

    def setHeader(self, name, value):
        self.headers[name] = value


class FakeRequest(object):
    def __init__(self, method="GET"):
        self.response = FakeResponse()
        self.environ = {"REQUEST_METHOD": method}


class TestAddCorsHeaders(unittest.TestCase):

    def test_no_origin_means_no_headers(self):
        req = FakeRequest()
        add_cors_headers(req, origin=None)
        self.assertEqual(req.response.headers, {})

    def test_string_origin_is_written_verbatim(self):
        req = FakeRequest()
        add_cors_headers(req, origin="https://app.example.com")
        self.assertEqual(
            req.response.headers["Access-Control-Allow-Origin"],
            "https://app.example.com")

    def test_callable_origin_receives_request(self):
        req = FakeRequest()
        captured = []

        def policy(request):
            captured.append(request)
            return "https://policy.example.com"

        add_cors_headers(req, origin=policy)
        self.assertEqual(captured, [req])
        self.assertEqual(
            req.response.headers["Access-Control-Allow-Origin"],
            "https://policy.example.com")

    def test_vary_origin_is_always_set_with_origin(self):
        req = FakeRequest()
        add_cors_headers(req, origin="https://a.example.com")
        self.assertEqual(req.response.headers["Vary"], "Origin")

    def test_default_methods_and_headers(self):
        req = FakeRequest()
        add_cors_headers(req, origin="*")
        self.assertIn("GET", req.response.headers["Access-Control-Allow-Methods"])
        self.assertIn("POST", req.response.headers["Access-Control-Allow-Methods"])
        self.assertIn("OPTIONS", req.response.headers["Access-Control-Allow-Methods"])
        self.assertIn("Authorization", req.response.headers["Access-Control-Allow-Headers"])
        self.assertIn("Content-Type", req.response.headers["Access-Control-Allow-Headers"])

    def test_custom_methods_and_headers(self):
        req = FakeRequest()
        add_cors_headers(
            req,
            origin="*",
            allow_methods=["GET"],
            allow_headers=["X-Custom"],
        )
        self.assertEqual(
            req.response.headers["Access-Control-Allow-Methods"], "GET")
        self.assertEqual(
            req.response.headers["Access-Control-Allow-Headers"], "X-Custom")

    def test_allow_credentials(self):
        req = FakeRequest()
        add_cors_headers(
            req, origin="https://app.example.com", allow_credentials=True)
        self.assertEqual(
            req.response.headers["Access-Control-Allow-Credentials"], "true")

    def test_max_age_is_serialized_as_string(self):
        req = FakeRequest()
        add_cors_headers(req, origin="*", max_age=600)
        self.assertEqual(
            req.response.headers["Access-Control-Max-Age"], "600")

    def test_no_request_context_does_not_crash(self):
        # add_cors_headers must not raise if it can't find a response.
        class _NoResp(object):
            pass
        add_cors_headers(_NoResp(), origin="*")


class TestCorsDecorator(unittest.TestCase):

    def test_get_response_carries_headers_and_calls_view(self):
        req = FakeRequest("GET")
        called = []

        @cors(origin="https://app.example.com")
        def view(context, request):
            called.append(True)
            return {"items": []}

        result = view(None, req)
        self.assertEqual(result, {"items": []})
        self.assertEqual(called, [True])
        self.assertEqual(
            req.response.headers["Access-Control-Allow-Origin"],
            "https://app.example.com")

    def test_options_preflight_short_circuits(self):
        req = FakeRequest("OPTIONS")
        called = []

        @cors(origin="https://app.example.com")
        def view(context, request):
            called.append(True)
            return {"should not": "be called"}

        result = view(None, req)
        self.assertEqual(result, {})
        self.assertEqual(called, [])
        self.assertIn(
            "Access-Control-Allow-Origin", req.response.headers)
        self.assertIn(
            "Access-Control-Allow-Methods", req.response.headers)

    def test_no_origin_means_no_headers_but_view_still_runs(self):
        req = FakeRequest("GET")

        @cors(origin=None)
        def view(context, request):
            return {"ok": True}

        self.assertEqual(view(None, req), {"ok": True})
        self.assertEqual(req.response.headers, {})


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAddCorsHeaders))
    suite.addTest(makeSuite(TestCorsDecorator))
    return suite
