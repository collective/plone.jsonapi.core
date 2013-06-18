# -*- coding: utf-8 -*-
#
# File: catalog.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import re
import logging

from zope import component
from zope import interface

from Products.CMFCore.utils import getToolByName
from plone.memoize.view import memoize_contextless
from Acquisition import aq_inner

from url import URL
from interfaces import IInfo
from interfaces import ICatalog

logger = logging.getLogger("plone.jsonapi::catalog")

REGEX = re.compile("[a-z0-9]{32}")


class Catalog(object):
    """ Plone API Catalog wrapper
    """
    interface.implements(ICatalog)

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request
        self._url_tool = None

    @property
    def url_tool(self):
        if self._url_tool is None:
            self._url_tool = component.getMultiAdapter(
                    (self.context, self.request),
                    name=u'api_url')
        return self._url_tool

    @property
    @memoize_contextless
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    @memoize_contextless
    def uid_catalog(self):
        return getToolByName(self.context, 'uid_catalog')

    def isUID(self, uid):
        if REGEX.match(uid):
            return True
        return False

    def search_uid(self, uid):
        brains = self.uid_catalog(UID=uid)

        if len(brains) == 0:
            return None
        if len(brains) > 1:
            raise ValueError("Got more than one result for an UID!")
        return brains[0]

    def search(self, query):
        """ execute catalog query

        Sanity checks if sort_limit is set and greater 0.
        Sniffs into the id key of the query to do a UID
        search instead
        """
        sort_limit = query.get("sort_limit", None)
        if sort_limit == 0:
            # sort_limit of 0 breaks the search
            del query["sort_limit"]

        brains = []
        id = query.get("id", None)

        if id is not None and self.isUID(id):
            logger.info("Received UID %s" % id)
            # portal catalog gives us also PloneGazette brains when searching
            # for an UID, WTF? Perhaps because they also manage some kind
            # of braindead catalog!
            # workaround: search first the uid catalog and then the portal
            # catalog with uid and id in query. We need a portal_catalog brain
            # because of the metadata!
            brain = self.search_uid(id)
            if brain is not None:
                # update the query with uid and id to get a unique result
                query.update({"id": brain.id, "UID": brain.UID})

        # search the portal catalog
        logger.info("Catalog Query=%r" % query)
        brains = self.portal_catalog(query)

        # if the id is given, we wakup the object an put in additional data
        # provided by the IInfo adapter
        wakeup_object = id is not None
        results = self.get_results(brains, wakeup_object)

        return dict(count=len(results),
                    items=results)

    def get_results(self, brains, wakeup_object=False):

        if brains is None:
            brains = []

        results = list()
        for brain in brains:
            info = self.brain_info(brain)

            # Wake up object and get object infos
            if wakeup_object:
                info.update(self.object_info(brain))

            # inject the api url
            info.update(self.url_tool.get_urls(brain))

            results.append(info)
        return results

    def brain_info(self, brain):
        """ infos extracted from the catalog brain
        """
        adapter = component.getAdapter(brain, IInfo, "braininfo")
        return adapter()

    def object_info(self, brain):
        """ infos extracted from the object
        """
        obj = brain.getObject()
        adapter = component.getAdapter(obj, IInfo, "objectinfo")
        return adapter()

# vim: set ft=python ts=4 sw=4 expandtab :
