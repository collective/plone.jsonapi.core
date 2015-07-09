# -*- coding: utf-8 -*-

from plone.jsonapi.core import router

from plone.jsonapi.core.tests.base import APITestCase


class TestSetup(APITestCase):
    """ Test URL registration machinery
    """

    def test_version(self):
        endpoint = "version"
        self.assertEqual(router.url_for(endpoint), "/plone/@@API/%s" % endpoint)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite
