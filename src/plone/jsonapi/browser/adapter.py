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
    """
    """
    interface.implements(IInfo)
    component.adapts(IATContentType)

    def __init__(self, context):
        self.context = context
        self.imageview = component.getMultiAdapter((context, context.REQUEST),
                name=u'images')

    def get_image_url(self, name):
        img = getattr(self.context, name, "")
        if img:
            return img.absolute_url()
        return img

    def get_scaled_image_url(self, name, scale="mini"):
        try:
            scaled = self.imageview.scale(name, scale=scale)
        except AttributeError:
            return ""
        if scaled is None:
            return ""
        return scaled.url

    def to_dict(self, obj):
        return {}

    def __call__(self):
        return self.to_dict(self.context)

# vim: set ft=python ts=4 sw=4 expandtab :
