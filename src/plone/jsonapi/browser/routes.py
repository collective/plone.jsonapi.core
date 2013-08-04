# -*- coding: utf-8 -*-
#
# File: routes.py

__author__ = 'Ramon Bartl <ramon.bartl@nexiles.de>'
__docformat__ = 'plaintext'

import logging

from zope import interface
from zope import component

from DateTime import DateTime

# local imports
from interfaces import IRouteProvider
from helpers import success

logger = logging.getLogger("plone.jsonapi.routes")

__version__ = 0.1
__build__ = 0
__date__ = "2013-06-17"


class PloneRoutes(object):
    interface.implements(IRouteProvider)

    ALLOWED_TYPES_TO_SEARCH = [
        "Document", "File", "Image", "Collection", "Event", "News Item",
    ]

    ALLOWED_SORT_INDEX = [
        "id", "created", "modified", "sortable_title", "start", "end",
        "getObjPositionInParent ", "expires", "Type",
    ]

    def initialize(self, context, request):
        """ Called by the API Framework
        """
        self.context = context
        self.request = request

        self._catalog = None

    @property
    def routes(self):
        return (
            ("/version", "version", self.json_version, dict(methods=['GET'])),
            ("/query", "query", self.json_query),
            ("/contents", "contents", self.json_contents),
            ("/contents/<string:content>", "contents", self.json_contents),
        )

    @property
    def catalog(self):
        if self._catalog is None:
            self._catalog = component.getMultiAdapter(
                    (self.context, self.request),
                    name=u'api_catalog')
        return self._catalog

    @property
    def portal(self):
        portal_state = component.getMultiAdapter((self.context, self.request),
                name=u'plone_portal_state')
        return portal_state.portal()

    @property
    def portal_path(self):
        return "/".join(self.portal.getPhysicalPath())

    def get_sort_on(self, request):
        """ returns the 'sort_on' from the request
        """
        sort_on = request.form.get("sort_on")
        if sort_on in self.ALLOWED_SORT_INDEX:
            return sort_on
        return "getObjPositionInParent"

    def get_sort_order(self, request):
        """ returns the 'sort_order' from the request
        """
        sort_order = request.form.get("sort_order")
        if sort_order in ["ascending", "a", "asc", "up", "high"]:
            return "ascending"
        if sort_order in ["descending", "d", "desc", "down", "low"]:
            return "descending"
        return "descending"

    def get_sort_limit(self, request):
        """ returns the 'sort_limit' from the request
        """
        limit = request.form.get("limit")
        if limit is None or not limit.isdigit():
            return None
        return int(limit)

    def get_portal_type(self, request):
        """ returns the 'portal_type' from the request
        """
        #portal_type = request.form.get("portal_type")
        #if portal_type in self.ALLOWED_TYPES_TO_SEARCH:
        #    return portal_type
        #return self.ALLOWED_TYPES_TO_SEARCH
        return self.portal.portal_types.keys()

    def get_start(self, request):
        """ returns the 'start' from the request
        """
        start = request.form.get("start")
        rng = request.form.get("range", "min")
        try:
            dt = DateTime(start)
        except:
            dt = DateTime()
        return dict(query=dt, range=rng)

    def get_query(self, request):
        """ returns the 'query' from the request
        """
        q = request.form.get("q", "")

        qs = q.lstrip("*.!$%&/()=#-+:'`´^")
        if qs and not qs.endswith("*"):
            qs += "*"
        return qs

    ###########################################################################
    # CUSTOM JSON METHODS
    ###########################################################################
    def json_contents(self, content=None):
        """ Return JSON for all content types
        """
        request = self.request
        query = {
                "sort_on": self.get_sort_on(request),
                "portal_type": self.get_portal_type(request),
                "sort_order": self.get_sort_order(request),
                "sort_limit": self.get_sort_limit(request),
                "SearchableText": self.get_query(request),
                }

        if content is not None:
            query.update({"id": content})

        results = self.catalog.search(query)
        return success("success", **results)

    def json_query(self):
        """ Query the Searchable Text Catalog only
        """
        request = self.request
        query = {
                "portal_type": self.get_portal_type(request),
                "sort_on": self.get_sort_on(request),
                "sort_order": self.get_sort_order(request),
                "sort_limit": self.get_sort_limit(request),
                "SearchableText": self.get_query(request),
                }

        logger.info("PloneJSONAPI::json_query:query=%r" % query)
        results = self.catalog.search(query)
        return success("success", **results)

    def json_version(self):
        """ return JSON API Version
        """
        logger.debug("json_version")
        response = dict(version=__version__,
                        build=__build__,
                        date=__date__)
        return response

# vim: set ft=python ts=4 sw=4 expandtab :
