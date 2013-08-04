# -*- coding: utf-8 -*-
#
# File: adapter.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import logging

from zope import interface

from DateTime.interfaces import IDateTime

from interfaces import IInfo

logger = logging.getLogger("plone.jsonapi.adapter")


class BrainInfo(object):
    """ Default Adapter for Catalog Brains.
    """
    interface.implements(IInfo)

    def __init__(self, brain):
        self.brain = brain
        # a mapping to specify the resource for this type.
        # For example: {'Documents': 'documents'}
        # will route the portal_type "Document" under the 'documents' URL
        # resource
        self.resources = {}

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
    """ Default Adapter for Plone content type objects.

    Gets called on an items detail page, e.g the leaf resource.
    Write custom adapters here to provide additional JSON data.
    """
    interface.implements(IInfo)

    def __init__(self, context):
        self.context = context

    def get_fields(self):
        out = []
        for field in self.context.schema.fields():
            if field.type == "object":
                logger.warning("Skipping object field %s" % field.getName())
                continue
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
