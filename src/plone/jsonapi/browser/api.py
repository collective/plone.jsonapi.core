# -*- coding: utf-8 -*-
#
# File: api.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import logging

from zope import component

from zope.interface import implements

from Products.Five import BrowserView
from zope.publisher.interfaces import IPublishTraverse

from decorators import runtime
from decorators import returns_json
from decorators import handle_errors

from interfaces import IAPI
from interfaces import IRouter

logger = logging.getLogger("plone.jsonapi")


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

    @handle_errors
    def dispatch(self):
        """ dispatches the given subpath to the router
        """
        path = "/".join(self.traverse_subpath)
        logger.info("Dispatching path: '%s'", path)
        for name, router in component.getUtilitiesFor(IRouter):
            router.initialize(self.context, self.request)
            if router.match(self.context, self.request, path):
                logger.info("Router '%r' will handle the request", router)
                return router(self.context, self.request, path)

    @returns_json
    @runtime
    def __call__(self):
        """ render json on __call__
        """
        return self.dispatch()

# vim: set ft=python ts=4 sw=4 expandtab :
