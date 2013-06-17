# -*- coding: utf-8 -*-
#
# File: url.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

from Acquisition import aq_inner
from zope.component import getMultiAdapter
from plone.memoize.view import memoize_contextless


class URL(object):
    """ Plone API URL Tool
    """

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request

        self.resources = {
                "Page": "pages",
                }

        self.additional_urls = {
                "orgas": ["reports", "events"],
                }

    @property
    @memoize_contextless
    def api_base_url(self):
        return self.portal.absolute_url() + "/@@API"

    def get_api_resource(self, brain, default="contents"):
        portal_type = brain.portal_type
        return self.resources.get(portal_type, default)

    def get_api_url(self, brain):
        base = self.api_base_url
        resource = self.get_api_resource(brain)
        uid = brain.UID
        return "%s/%s/%s" % (base, resource, uid)

    def get_urls(self, brain):
        out = dict()
        api_url = self.get_api_url(brain)

        resource = self.get_api_resource(brain)

        for url in self.additional_urls.get(resource, []):
            out["api_url_" + url] = api_url + "/" + url

        out["api_url"] = api_url

        return out

# vim: set ft=python ts=4 sw=4 expandtab :
