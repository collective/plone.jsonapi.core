# -*- coding: utf-8 -*-
#
# File: url.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

from zope import interface
from zope import component

from plone.memoize.view import memoize_contextless

from interfaces import IURL
from interfaces import IInfo


class URL(object):
    """ Plone API URL Tool
    """
    interface.implements(IURL)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal(self):
        portal_state = component.getMultiAdapter((self.context, self.request),
                name=u'plone_portal_state')
        return portal_state.portal()

    @property
    @memoize_contextless
    def api_base_url(self):
        return self.portal.absolute_url() + "/@@API"

    def get_api_resource(self, brain, default="contents"):
        adapter = component.getAdapter(brain, IInfo, name="braininfo")
        portal_type = brain.portal_type
        return adapter.resources.get(portal_type, default)

    def get_api_url(self, brain):
        base = self.api_base_url
        resource = self.get_api_resource(brain)
        uid = brain.UID
        return "%s/%s/%s" % (base, resource, uid)

    def get_urls(self, brain):
        api_url = self.get_api_url(brain)
        return {"api_url": api_url}

# vim: set ft=python ts=4 sw=4 expandtab :
