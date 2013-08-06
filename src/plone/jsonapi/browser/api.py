# -*- coding: utf-8 -*-
#
# File: api.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import logging

from zope import interface
from zope import component

from zope.interface import implements
from zope.component import getUtility
from zope.component import getUtilitiesFor

from Products.Five import BrowserView
from zope.publisher.interfaces import IPublishTraverse

from decorators import runtime
from decorators import returns_json
from decorators import handle_errors

from interfaces import IAPI
from interfaces import IRouter
from interfaces import IRouteProvider

logger = logging.getLogger("plone.jsonapi")


class API(BrowserView):
    """ JSON API Framework
    """
    implements(IAPI, IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self._router = None
        self.traverse_subpath = []
        self.register()

    @property
    def router(self):
        if self._router is None:
            self._router = component.getMultiAdapter(
                    (self.context, self.request),
                    name=u'api_router')
        return self._router

    def register(self):
        """ queries all route prviders and initialize them
        """
        providers = getUtilitiesFor(IRouteProvider)
        for name, instance in providers:

            # 1. initialize the route provider with the context and request
            # XXX: this should be removed
            if getattr(instance, "initialize", False):
                instance.initialize(self.context, self.request)

            routes = instance.routes
            if callable(instance.routes):
                routes = instance.routes()

            # 2. add the provided routes to the router
            for route in routes:
                self.router.add_url_rule(*route)

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
        return self.router(self.context, self.request, path)

    @returns_json
    @runtime
    def __call__(self):
        """ render json on __call__
        """
        return self.dispatch()

# vim: set ft=python ts=4 sw=4 expandtab :
