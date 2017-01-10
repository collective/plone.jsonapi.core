# -*- coding: utf-8 -*-

import logging

from zope import component

from zope.interface import implements

from Products.Five import BrowserView
from zope.publisher.interfaces import IPublishTraverse

from decorators import runtime
from decorators import returns_xml
from decorators import returns_json
from decorators import returns_binary_stream
from decorators import handle_errors

from interfaces import IAPI
from interfaces import IRouter

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


logger = logging.getLogger("plone.jsonapi.core.api")


class API(BrowserView):
    """ JSON API Framework
    """
    implements(IAPI, IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        """ get's called before __call__ for each path name
        """
        self.traverse_subpath.append(name)
        return self

    def dispatch(self):
        """ dispatches the given subpath to the router
        """
        path = "/".join(self.traverse_subpath)
        logger.debug("Dispatching path: '%s'", path)
        for name, router in component.getUtilitiesFor(IRouter):
            router.initialize(self.context, self.request)
            # The first router which is able to match the route wins.
            if router.match(self.context, self.request, path):
                logger.debug("Router '%r' will handle the request", router)
                return router(self.context, self.request, path)

    @returns_json
    @runtime
    @handle_errors
    def to_json(self):
        return self.dispatch()

    @returns_binary_stream
    def to_binary_stream(self):
        return self.dispatch()

    @returns_xml
    def to_xml(self):
        return self.dispatch()

    def __call__(self):
        """ render json on __call__
        """
        accept = self.request.getHeader("Accept")
        if self.request.form.get("asbinary", False) or accept == "application/zip":
            return self.to_binary_stream()
        if self.request.form.get("asxml", False) or accept == "application/xml":
            return self.to_xml()
        # return JSON per default
        return self.to_json()
