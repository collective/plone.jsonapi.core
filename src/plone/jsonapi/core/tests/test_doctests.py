# -*- coding: utf-8 -*-

import doctest

import unittest2 as unittest

from plone.testing.z2 import Browser

from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing.layers import IntegrationTesting
from zope.configuration import xmlconfig

from Testing import ZopeTestCase as ztc


class TestLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.jsonapi.core
        xmlconfig.file('configure.zcml', plone.jsonapi.core,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        login(portal, 'admin')


TEST_FIXTURE = TestLayer()
INTEGRATION_TESTING = IntegrationTesting(bases=(TEST_FIXTURE,),
                          name="plone.jsonapi.core:Integration")


class APITestCase(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app     = self.layer.get("app")
        self.portal  = self.layer.get("portal")

    def getBrowser(self, handleErrors=False):
        browser = Browser(self.app)
        if handleErrors:
            browser.handleErrors = True
        return browser


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        ztc.ZopeDocFileSuite(
            '../docs/Readme.txt',
            test_class=APITestCase,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        ),
    ])
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
