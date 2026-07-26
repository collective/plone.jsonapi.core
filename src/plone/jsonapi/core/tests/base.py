# -*- coding: utf-8 -*-

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing.layers import IntegrationTesting
from plone.testing import z2
from plone.testing.z2 import Browser
from zope.configuration import xmlconfig

import json
import os
import unittest2 as unittest


class TestLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.jsonapi.core

        xmlconfig.file(
            "configure.zcml", plone.jsonapi.core, context=configurationContext
        )

        # Install product and call its initialize() function
        z2.installProduct(app, "plone.jsonapi.core")

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, "plone.jsonapi.core")

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ["Manager"])

        # Test fixture -- p.j.c. needs to have a request
        from plone.jsonapi.core import router

        router.DefaultRouter.initialize(portal, portal.REQUEST)


TEST_FIXTURE = TestLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(TEST_FIXTURE,), name="plone.jsonapi.core:Integration"
)


class APITestCase(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        super(APITestCase, self).setUp()
        from zope.globalrequest import setRequest
        # url_for derives the @@API mount from the *current* request
        # (via zope.globalrequest). In this minimal layer nothing
        # publishes an @@API request for the integration tests, so
        # expose a request whose URL points at the @@API view and make
        # it the global request. Full Plone wires this up automatically;
        # here we do it explicitly so url_for can resolve.
        request = self.layer["request"]
        api_url = self.getPortal().absolute_url() + "/@@API"
        request["URL"] = api_url
        request["ACTUAL_URL"] = api_url
        setRequest(request)

    def tearDown(self):
        from zope.globalrequest import clearRequest
        clearRequest()
        super(APITestCase, self).tearDown()

    def getBrowser(self, handleErrors=False):
        browser = Browser(self.getApp())
        if handleErrors:
            browser.handleErrors = True
        return browser

    def getApp(self):
        return self.layer.get("app")

    def getPortal(self):
        return self.layer.get("portal")

    def getRequest(self):
        return self.layer.get("request")

    def decode(self, s):
        return json.loads(s)

    def get_testfile_path(self):
        return os.path.join(os.path.dirname(__file__), "plone.pdf")
