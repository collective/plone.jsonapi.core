# -*- coding: utf-8 -*-

"""Unit tests for the WebDAV verb bypass subscriber."""

import unittest2 as unittest

from plone.jsonapi.core.browser.webdav import allow_api_verbs
from plone.jsonapi.core.browser.webdav import is_api_request


class FakeRequest(object):
    def __init__(self, method="GET", path_info="/"):
        self._data = {"REQUEST_METHOD": method, "PATH_INFO": path_info}
        # Zope's default; the subscriber may flip it to 0.
        self.maybe_webdav_client = 1

    def get(self, key, default=None):
        return self._data.get(key, default)


class FakeEvent(object):
    def __init__(self, request):
        self.request = request


class TestIsApiRequest(unittest.TestCase):

    def test_matches_explicit_view_segment(self):
        self.assertTrue(is_api_request("/plone/@@API/senaite/v1/x"))

    def test_matches_acquisition_form_segment(self):
        self.assertTrue(is_api_request("/plone/API/senaite/v1/x"))

    def test_no_match_for_plain_content(self):
        self.assertFalse(is_api_request("/plone/clients/client-1"))

    def test_no_substring_false_positive(self):
        # "APIfolder" is not the "API" segment.
        self.assertFalse(is_api_request("/plone/APIfolder/doc"))


class TestAllowApiVerbs(unittest.TestCase):

    def test_patch_to_api_clears_flag(self):
        req = FakeRequest("PATCH", "/plone/@@API/senaite/v1/uid")
        allow_api_verbs(FakeEvent(req))
        self.assertEqual(req.maybe_webdav_client, 0)

    def test_put_to_api_clears_flag(self):
        req = FakeRequest("PUT", "/plone/@@API/senaite/v1/uid")
        allow_api_verbs(FakeEvent(req))
        self.assertEqual(req.maybe_webdav_client, 0)

    def test_delete_to_api_clears_flag(self):
        req = FakeRequest("DELETE", "/plone/@@API/senaite/v1/uid")
        allow_api_verbs(FakeEvent(req))
        self.assertEqual(req.maybe_webdav_client, 0)

    def test_get_is_untouched(self):
        req = FakeRequest("GET", "/plone/@@API/senaite/v1/uid")
        allow_api_verbs(FakeEvent(req))
        self.assertEqual(req.maybe_webdav_client, 1)

    def test_post_is_untouched(self):
        req = FakeRequest("POST", "/plone/@@API/senaite/v1/uid")
        allow_api_verbs(FakeEvent(req))
        self.assertEqual(req.maybe_webdav_client, 1)

    def test_put_to_non_api_is_untouched(self):
        # A genuine WebDAV PUT to content must keep its flag so real
        # WebDAV keeps working.
        req = FakeRequest("PUT", "/plone/clients/client-1")
        allow_api_verbs(FakeEvent(req))
        self.assertEqual(req.maybe_webdav_client, 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIsApiRequest))
    suite.addTest(makeSuite(TestAllowApiVerbs))
    return suite
