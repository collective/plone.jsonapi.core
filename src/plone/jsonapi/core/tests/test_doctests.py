# -*- coding: utf-8 -*-

import doctest

import unittest2 as unittest

from Testing import ZopeTestCase as ztc

from plone.jsonapi.core.tests.base import APITestCase


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
