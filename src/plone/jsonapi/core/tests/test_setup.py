# -*- coding: utf-8 -*-

from plone.jsonapi.core import router
from plone.jsonapi.core.tests.base import APITestCase


class TestSetup(APITestCase):
    """ Test URL registration machinery
    """

    def test_version(self):
        self.assertEqual(router.url_for("apiversion"), "/plone/@@API/version")


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite
