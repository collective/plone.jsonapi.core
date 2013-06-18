# -*- coding: utf-8 -*-
#
# File: adapter.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

from zope import interface
from zope import component

from Products.ATContentTypes.interface.interfaces import IATContentType

from interfaces import IInfo


class BaseInfo(object):
    """ Default Adapter for ATContent Types.

    Gets called on an items detail page, e.g the leaf resource.
    Write custom adapters here to provide additional JSON data.
    """
    interface.implements(IInfo)
    component.adapts(IATContentType)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return {}

# vim: set ft=python ts=4 sw=4 expandtab :
