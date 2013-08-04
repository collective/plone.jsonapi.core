# -*- coding: utf-8 -*-
#
# File: router.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import logging

from zope import interface
from werkzeug.routing import Map, Rule

from interfaces import IRouter

logger = logging.getLogger("plone.jsonapi.router")


class Router(object):
    """ API Router Tool
    """
    interface.implements(IRouter)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.rule_class = Rule
        self.view_functions = {}
        self.url_map = Map()

    def add_url_rule(self, rule, endpoint=None, view_func=None, options=None):
        if endpoint is None:
            endpoint = view_func.__name__

        old_func = self.view_functions.get(endpoint)
        if old_func is not None and old_func != view_func:
            raise AssertionError('View function mapping is overwriting an '
                                 'existing endpoint function: %s' % endpoint)

        self.view_functions[endpoint] = view_func

        if options is None:
            return self.url_map.add(self.rule_class(rule, endpoint=endpoint))

        return self.url_map.add(self.rule_class(rule, endpoint=endpoint, **options))

    @property
    def servername(self):
        server_name = self.request.get("SERVER_NAME")
        server_port = self.request.get("SERVER_PORT")
        return "%s:%s" % (server_name, server_port)

    def get_adapter(self, path_info):
        # get the adapter to match the url to a function
        adapter = self.url_map.bind(
                self.servername, path_info=path_info)
        return adapter

    def __call__(self, path):
        """ calls the matching view function for the given path
        """
        method = self.request.method
        logger.info("router.__call__: method=%s" % method)
        adapter = self.get_adapter(path)
        endpoint, values = adapter.match(method=method)
        return self.view_functions[endpoint](**values)

# vim: set ft=python ts=4 sw=4 expandtab :
