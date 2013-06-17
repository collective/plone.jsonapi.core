# -*- coding: utf-8 -*-
#
# File: api.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import time
import logging
import simplejson as json

from werkzeug.exceptions import HTTPException

from DateTime import DateTime

from zope.interface import implements
from zope.component import getMultiAdapter

from Products.Five import BrowserView

from zope.publisher.interfaces import IPublishTraverse


from plone.jsonapi.browser.interfaces import IPloneJSONAPI
from plone.jsonapi.browser.router import Router
from plone.jsonapi.browser.catalog import Catalog


logger = logging.getLogger("plone.jsonapi")

__version__ = 0.1
__build__ = 0
__date__ = "2013-06-17"


def error(message, **kw):
    logger.error("API ERROR: %s, kw=%r" % (message, kw))
    result = {"success": False, "error": message}
    if kw:
        result.update(kw)
    return result


def success(message, **kw):
    result = {"success": True,
            "message": message}
    if kw:
        result.update(kw)

    return result


class API(BrowserView):
    """ Plone JSON API
    """
    implements(IPloneJSONAPI, IPublishTraverse)

    ALLOWED_TYPES_TO_SEARCH = [
        "Document", "File", "Image", "Collection", "Event", "News Item",
    ]

    ALLOWED_SORT_INDEX = [
        "id", "created", "modified", "sortable_title", "start", "end",
        "getObjPositionInParent ", "expires", "Type",
    ]

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.traverse_subpath = []

        self.router = Router(context, request)
        self.catalog = Catalog(context, request)

    def publishTraverse(self, request, name):
        """ get's called before __call__ for each path name
        """
        self.traverse_subpath.append(name)
        return self

    def __call__(self):
        """ render json on __call__
        """
        return self.render()

    def dispatch_request(self, request):
        """ Maps the request to a endpoint (method).

           uses a werkzeug adapter to match the route.
        """

        # get the adapter to match the url to a function
        path_info = "/".join(self.traverse_subpath)
        adapter = self.router.get_adapter(path_info)

        try:
            endpoint, values = adapter.match()
            return getattr(self, 'json_' + endpoint)(request, **values)
        except HTTPException, e:
            return error(e.__str__())

    def render(self):
        """ render the dumped json
        """
        self.request.response.setHeader("Content-Type", "application/json")

        # execute method with time measure
        start = time.time()
        result = self.dispatch_request(self.request)
        end = time.time()

        result.update(dict(_runtime=end - start))

        # XXX: add cache headers!
        response = json.dumps(result)

        # enable jsonp
        c = self.request.form.get("c", None)
        if c is not None:
            return "%s(%s);" % (str(c), response)

        return response

    @property
    def portal(self):
        portal_state = getMultiAdapter((self.context, self.request),
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
        portal_type = request.form.get("portal_type")
        if portal_type in self.ALLOWED_TYPES_TO_SEARCH:
            return portal_type
        return self.ALLOWED_TYPES_TO_SEARCH

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

    def json_contents(self, request, content=None):
        """ Return JSON for all content types
        """
        query = {
                "sort_on": self.get_sort_on(request),
                "portal_type": self.get_portal_type(request),
                "sort_order": self.get_sort_order(request),
                "sort_limit": self.get_sort_limit(request),
                "SearchableText": self.get_query(request),
                }

        if content:
            query.update({"id": content})

        results = self.catalog.search(query)
        return success("success", **results)

    def json_query(self, request):
        """ Query the Searchable Text Catalog only
        """
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

    def json_version(self, request):
        """ return JSON API Version
        """
        logger.debug("json_version")
        response = dict(version=__version__,
                        build=__build__,
                        date=__date__)
        return response

# vim: set ft=python ts=4 sw=4 expandtab :
