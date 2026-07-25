# -*- coding: utf-8 -*-

"""Unit tests for the swappable error handler.

Covers the default_error_handler in isolation and the handle_errors
decorator behavior. The full Plone fixture is not needed for these
paths; the decorator only touches request.response.setStatus.
"""

import unittest2 as unittest

from plone.jsonapi.core.browser.decorators import default_error_handler
from plone.jsonapi.core.browser.decorators import handle_errors
from plone.jsonapi.core.browser.exceptions import APIError
from plone.jsonapi.core.browser.exceptions import NotFoundError


class FakeResponse(object):
    def __init__(self):
        self.status = None

    def setStatus(self, status):
        self.status = status


class FakeRequest(object):
    def __init__(self):
        self.response = FakeResponse()


class TestDefaultErrorHandler(unittest.TestCase):

    def test_message_is_the_exception_message_only(self):
        request = FakeRequest()
        result = default_error_handler(ValueError("visible"), request)
        self.assertEqual(result["message"], "visible")
        self.assertFalse(result["success"])

    def test_no_traceback_leaks_into_message(self):
        # Regression: pre-refactor default put format_exc() in message.
        request = FakeRequest()
        result = default_error_handler(RuntimeError("boom"), request)
        self.assertNotIn("Traceback", result["message"])
        self.assertNotIn("File \"", result["message"])
        self.assertNotIn("line ", result["message"])

    def test_type_field_is_exception_class_name(self):
        request = FakeRequest()
        result = default_error_handler(KeyError("missing"), request)
        self.assertEqual(result["type"], "KeyError")

    def test_status_from_APIError_subclass(self):
        request = FakeRequest()
        default_error_handler(NotFoundError("gone"), request)
        self.assertEqual(request.response.status, 404)

    def test_status_defaults_to_500_for_bare_exception(self):
        request = FakeRequest()
        default_error_handler(RuntimeError("boom"), request)
        self.assertEqual(request.response.status, 500)

    def test_explicit_status_on_APIError_wins(self):
        request = FakeRequest()
        default_error_handler(APIError("teapot", status=418), request)
        self.assertEqual(request.response.status, 418)

    def test_no_request_context_does_not_crash(self):
        # Unit tests and setup handlers may raise without a request.
        result = default_error_handler(NotFoundError("gone"), None)
        self.assertEqual(result["message"], "gone")


class TestHandleErrorsDecorator(unittest.TestCase):

    def _fake_view(self):
        class View(object):
            request = FakeRequest()
        return View()

    def test_successful_call_passes_through(self):
        view = self._fake_view()

        @handle_errors
        def ok(self):
            return {"success": True, "items": [1, 2, 3]}

        self.assertEqual(ok(view), {"success": True, "items": [1, 2, 3]})

    def test_APIError_produces_envelope_with_type_and_status(self):
        view = self._fake_view()

        @handle_errors
        def raiser(self):
            raise NotFoundError("no widget")

        result = raiser(view)
        self.assertEqual(result["message"], "no widget")
        self.assertEqual(result["type"], "NotFoundError")
        self.assertFalse(result["success"])
        self.assertEqual(view.request.response.status, 404)

    def test_bare_exception_produces_500(self):
        view = self._fake_view()

        @handle_errors
        def raiser(self):
            raise RuntimeError("boom")

        result = raiser(view)
        self.assertEqual(result["type"], "RuntimeError")
        self.assertEqual(view.request.response.status, 500)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDefaultErrorHandler))
    suite.addTest(makeSuite(TestHandleErrorsDecorator))
    return suite
