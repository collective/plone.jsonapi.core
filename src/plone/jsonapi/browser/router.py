# -*- coding: utf-8 -*-
#
# File: router.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import logging

from zope import interface
from zope import event
from zope import component
from werkzeug.routing import Map, Rule

from interfaces import IRouter
from interfaces import IRouteProvider

logger = logging.getLogger("plone.jsonapi.router")

class Router(object):

    def __init__(self):
        logger.info("DefaultRouter::__init__")
        self.rule_class = Rule
        self.view_functions = {}
        self.url_map = Map()
        self.is_initialized = False

    def initialize(self, *args, **kw):
        if self.is_initialized:
            return
        logger.info("DefaultRouter::initialize")
        for name, provider in component.getUtilitiesFor(IRouteProvider):
            logger.info("DefaultRouter::initialize: name=%s, provider=%r", name, provider)

            if getattr(provider, "initialize", None):
                provider.initialize(*args, **kw)

            for route in provider.routes:
                self.add_url_rule(*route)

        self.is_initialized = True


    def add_url_rule(self, rule, endpoint=None, view_func=None, options=None):
        """ adds a rule to the url map

        :param rule:      the url rule, e.g /version
        :param endpoint:  the name of the rule, e.g version
        :param endpoint:  The endpoint for this rule. This can be anything
        :param options:   additional options to be passed to the router
        """
        logger.info("DefaultRouter.add_url_rule: %s (%s) -> %r options: %r", rule, endpoint, view_func.func_name, options)
        if endpoint is None:
            endpoint = view_func.__name__

        old_func = self.view_functions.get(endpoint)
        if old_func is not None and old_func != view_func:
            raise AssertionError('View function mapping is overwriting an '
                                 'existing endpoint function: %s' % endpoint)

        self.view_functions[endpoint] = view_func

        if options is None:
            # http://werkzeug.pocoo.org/docs/routing/#werkzeug.routing.Rule
            return self.url_map.add(self.rule_class(rule, endpoint=endpoint))

        return self.url_map.add(self.rule_class(rule, endpoint=endpoint, **options))

    def servername(self, request):
        server_name = request.get("SERVER_NAME")
        server_port = request.get("SERVER_PORT")
        return "%s:%s" % (server_name, server_port)

    def get_adapter(self, servername, path_info):
        # get the adapter to match the url to a function
        adapter = self.url_map.bind(servername, path_info=path_info)
        return adapter

    def match(self, context, request, path):
        method = request.method
        logger.info("router.match: method=%s" % method)
        adapter = self.get_adapter(self.servername(request), path)

        endpoint, values = adapter.match(method=method)
        return endpoint, values

    def __call__(self, context, request, path):
        """ calls the matching view function for the given path
        """
        logger.info("router.__call__: path=%s" % path)

        endpoint, values = self.match(context, request, path)

        return self.view_functions[endpoint](context, request, **values)


DefaultRouter = Router()

def DefaultRouterFactory():
    logger.info("DefaultRouterFactory")
    return DefaultRouter


def add_route(rule, endpoint=None, **kw):
    def wrapper(f):
        DefaultRouter.add_url_rule(rule, endpoint=endpoint, view_func=f, options=kw)
        return f
    return wrapper


# vim: set ft=python ts=4 sw=4 expandtab :
