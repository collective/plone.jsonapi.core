# -*- coding: utf-8 -*-
#
# File: adapter.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

from zope import interface
from zope import component

from DateTime.interfaces import IDateTime
from Products.ATContentTypes.interface.interfaces import IATContentType

from interfaces import IInfo


class BrainInfo(object):
    """ Default Adapter for Catalog Brains.
    """
    interface.implements(IInfo)
    component.adapts(interface.Interface)

    def __init__(self, brain):
        self.brain = brain

    def __call__(self):
        """ infos extracted from the catalog brain
        """
        brain = self.brain
        return {
            "id": brain.getId,
            "title": brain.Title,
            "description": brain.Description,
            "url": brain.getURL(),
            "portal_type": brain.portal_type,
            "created": brain.created.ISO8601(),
            "modified": brain.modified.ISO8601(),
            "effective": brain.effective.ISO8601(),
            "type": brain.portal_type,
            "tags": brain.subject,
        }


class ObjectInfo(object):
    """ Default Adapter for ATContent Type Objects.

    Gets called on an items detail page, e.g the leaf resource.
    Write custom adapters here to provide additional JSON data.
    """
    interface.implements(IInfo)
    component.adapts(IATContentType)

    def __init__(self, context):
        self.context = context

    def get_fields(self):
        out = []
        for field in self.context.schema.fields():
            out.append({
                "name": field.getName(),
                "type": field.type,
                "data": self.get_data(field),
            })
        return out

    def get_data(self, field):
        data = field.get(self.context)
        if IDateTime.providedBy(data):
            return data.ISO8601()
        return data

    def __call__(self):
        return {
            "fields": self.get_fields(),
        }


# vim: set ft=python ts=4 sw=4 expandtab :
