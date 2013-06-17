# -*- coding: utf-8 -*-
#
# File: catalog.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import re
import logging

from Products.CMFCore.utils import getToolByName
from plone.memoize.view import memoize_contextless
from Acquisition import aq_inner

from plone.jsonapi.browser.interfaces import IInfo
from plone.jsonapi.browser.url import URL

logger = logging.getLogger("plone.jsonapi::catalog")

REGEX = re.compile("[a-z0-9]{32}")


class Catalog(object):
    """ Plone API Catalog wrapper
    """

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request
        self.url = URL(context, request)

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
            # for an Orga UID, WTF? Perhaps because they also manage some kind
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

        with_object_info = id is not None
        results = self.get_results(brains, with_object_info)

        return dict(count=len(results),
                    items=results)

    def get_results(self, brains, with_object_info):
        if brains is None: brains = []

        results = list()
        for brain in brains:
            wrapper = Brain(brain)
            info = wrapper.to_dict(with_object_info)
            info.update(self.url.get_urls(brain))
            results.append(info)
        return results


class Brain(object):
    """ simple brain wrapper
    """

    def __init__(self, brain):
        self.brain = brain

    @property
    def brain_info(self):
        brain = self.brain
        return dict(
            id = brain.getId,
            title = brain.Title,
            description = brain.Description,
            url = brain.getURL(),
            portal_type = brain.portal_type,
            created = brain.created.ISO8601(),
            modified = brain.modified.ISO8601(),
            effective = brain.effective.ISO8601(),
            type = brain.portal_type,
            tags = brain.subject,
        )

    @property
    def object_info(self):
        obj = self.brain.getObject()
        adapter = IInfo(obj)
        return adapter()

    def to_dict(self, with_object_info):
        info = self.brain_info
        if with_object_info:
            info.update(self.object_info)
        return info

# vim: set ft=python ts=4 sw=4 expandtab :
