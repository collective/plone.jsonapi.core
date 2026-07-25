# -*- coding: utf-8 -*-

from plone.jsonapi.core import router
from plone.jsonapi.core.tests.base import APITestCase


class TestSetup(APITestCase):
    """ Test URL registration machinery
    """

    def test_version(self):
        self.assertEqual(router.url_for("apiversion"), "/plone/@@API/version")

    def test_url_for_force_external(self):
        # force_external must return an absolute URL for the current host.
        url = router.url_for("apiversion", force_external=True)
        self.assertTrue(url.startswith("http://"), url)
        self.assertTrue(url.endswith("/@@API/version"), url)


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite
