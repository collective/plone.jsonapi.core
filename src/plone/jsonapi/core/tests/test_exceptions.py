# -*- coding: utf-8 -*-

"""Unit tests for the APIError hierarchy.

Pins the class layout (base + typed subclasses, default status codes,
message/status behavior) so refactors don't silently change the shape
downstream consumers depend on.
"""

import unittest2 as unittest

from plone.jsonapi.core.browser.exceptions import APIError
from plone.jsonapi.core.browser.exceptions import BadRequestError
from plone.jsonapi.core.browser.exceptions import ConflictError
from plone.jsonapi.core.browser.exceptions import ForbiddenError
from plone.jsonapi.core.browser.exceptions import MethodNotAllowedError
from plone.jsonapi.core.browser.exceptions import NotFoundError
from plone.jsonapi.core.browser.exceptions import UnauthorizedError
from plone.jsonapi.core.browser.exceptions import ValidationError


class TestAPIErrorHierarchy(unittest.TestCase):

    def test_every_typed_error_subclasses_APIError(self):
        # Any `except APIError:` handler must catch every subclass so
        # downstream code that predates the hierarchy keeps working.
        for cls in (BadRequestError, UnauthorizedError, ForbiddenError,
                    NotFoundError, MethodNotAllowedError, ConflictError,
                    ValidationError):
            self.assertTrue(
                issubclass(cls, APIError),
                "{} must inherit from APIError".format(cls.__name__))

    def test_default_status_per_subclass(self):
        self.assertEqual(APIError.status, 500)
        self.assertEqual(BadRequestError.status, 400)
        self.assertEqual(UnauthorizedError.status, 401)
        self.assertEqual(ForbiddenError.status, 403)
        self.assertEqual(NotFoundError.status, 404)
        self.assertEqual(MethodNotAllowedError.status, 405)
        self.assertEqual(ConflictError.status, 409)
        self.assertEqual(ValidationError.status, 422)

    def test_message_survives_str(self):
        self.assertEqual(str(NotFoundError("no such thing")), "no such thing")

    def test_explicit_status_overrides_class_default(self):
        err = ForbiddenError("nope", status=451)
        self.assertEqual(err.status, 451)

    def test_message_attribute_is_set(self):
        err = ValidationError("bad payload")
        self.assertEqual(err.message, "bad payload")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAPIErrorHierarchy))
    return suite
