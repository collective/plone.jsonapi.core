# -*- coding: utf-8 -*-

import logging
from urlparse import urlsplit

from zope import component
from werkzeug.routing import Map, Rule

from interfaces import IRouteProvider

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

logger = logging.getLogger("plone.jsonapi.core.router")


class Router(object):
    """ API Router
    """

    def __init__(self):
        logger.debug("DefaultRouter::__init__")
        self.rule_class = Rule
        self.view_functions = {}
        self.url_map = Map()
        self.is_initialized = False
        self.http_host = ""

    def initialize(self, context, request):
        """ called by the API Framework
        """
        logger.debug("DefaultRouter.initialize: context=%r request=%r" % (context, request))

        self.context = context
        self.request = request

        self.environ = request.environ
        self.http_host = urlsplit(request.get("ACTUAL_URL", "")).netloc
        self.url = request.getURL()

        if self.is_initialized:
            return

        logger.debug("DefaultRouter::initialize")
        for name, provider in component.getUtilitiesFor(IRouteProvider):
            logger.debug("DefaultRouter::initialize: name=%s, provider=%r", name, provider)

            if getattr(provider, "initialize", None):
                provider.initialize(context, request)

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
        logger.debug("DefaultRouter.add_url_rule: %s (%s) -> %r options: %r", rule, endpoint, view_func.func_name, options)
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

    def get_adapter(self, **options):
        """ return a new werkzeug map adapter

        default options:
        (script_name=None, subdomain=None, url_scheme='http', default_method='GET', path_info=None, query_args=None)
        see: http://werkzeug.pocoo.org/docs/routing/#werkzeug.routing.Map.bind
        """
        adapter = self.url_map.bind(self.http_host, **options)
        return adapter

    def match(self, context, request, path):
        """ url matcher

        default options:
        (path_info=None, method=None, return_rule=False, query_args=None)
        see: http://werkzeug.pocoo.org/docs/routing/#werkzeug.routing.MapAdapter.match
        """
        method = request.environ.get("REQUEST_METHOD", "GET")
        logger.debug("router.match: method=%s" % method)
        adapter = self.get_adapter(path_info=path)
        endpoint, values = adapter.match(method=method)
        return endpoint, values

    def url_for(self, endpoint, **options):
        """ get the url for the endpoint

        default options:
        (values=None, method=None, force_external=False, append_unknown=True)
        see: http://werkzeug.pocoo.org/docs/routing/#werkzeug.routing.MapAdapter.build
        """

        # XXX: this is all a little bit hacky, especially when it comes to virtual hosting.

        spp = self.request.physicalPathFromURL(self.url)

        # find the API view root
        path = []
        for el in spp:
            path.append(el)
            if el == "API" or el == "@@API":
                break

        virt_path = self.request.physicalPathToVirtualPath(path)
        script_name = self.request.physicalPathToURL(virt_path, relative=1)

        adapter = self.get_adapter(script_name=script_name)
        return adapter.build(endpoint, **options)

    def __call__(self, context, request, path):
        """ calls the matching view function for the given path
        """
        logger.debug("router.__call__: path=%s" % path)

        endpoint, values = self.match(context, request, path)
        return self.view_functions[endpoint](context, request, **values)


DefaultRouter = Router()

def DefaultRouterFactory():
    logger.debug("DefaultRouterFactory")
    return DefaultRouter


#-----------------------------------------------------------------------------
# Exposed Router API
#-----------------------------------------------------------------------------

def add_route(rule, endpoint=None, **kw):
    """ wrapper to add an url rule

    Example:

    >>> from plone.jsonapi import router
    >>> @router.add_route("/hello/<string:name>", "hello", methods=["GET"])
    ... def hello(context, request, name="world"):
    ...     return dict(hello=name)
    """
    def wrapper(f):
        DefaultRouter.add_url_rule(rule, endpoint=endpoint, view_func=f, options=kw)
        return f
    return wrapper


def url_for(endpoint, **options):
    """ method to retrieve the API URL of an endpoint

    Example::

    >>> from plone.jsonapi import router
    >>> router.url_for("hello", values={"name": "jsonapi"}, force_external=True)
    """
    return DefaultRouter.url_for(endpoint, **options)
