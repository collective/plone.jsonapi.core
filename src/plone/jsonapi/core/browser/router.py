# -*- coding: utf-8 -*-

from .exceptions import MethodNotAllowedError
from .exceptions import NotFoundError
from .interfaces import IRouteProvider
from six.moves.urllib.parse import urlsplit
from werkzeug.exceptions import MethodNotAllowed as WzMethodNotAllowed
from werkzeug.exceptions import NotFound as WzNotFound
from werkzeug.routing import Map
from werkzeug.routing import Rule
from zope import component
from zope.globalrequest import getRequest

import logging


__author__ = "Ramon Bartl <rb@ridingbytes.com>"
__docformat__ = "plaintext"

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

    def initialize(self, context, request):
        """Build the route table once from the registered IRouteProvider
        utilities.

        The router is a process-global singleton shared across request
        threads, so it deliberately stores NO per-request state. Anything
        derived from the current request (host, scheme, URL) is read from
        the thread-local request at call time -- see `get_adapter` and
        `url_for` -- so concurrent requests on different virtual hosts or
        schemes cannot clobber each other.
        """
        if self.is_initialized:
            return

        logger.debug("DefaultRouter::initialize")
        for name, provider in component.getUtilitiesFor(IRouteProvider):
            logger.debug(
                "DefaultRouter::initialize: name=%s, provider=%r",
                name, provider,
            )

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
        logger.debug(
            "DefaultRouter.add_url_rule: %s (%s) -> %r options: %r",
            rule,
            endpoint,
            view_func.__name__,
            options,
        )
        if endpoint is None:
            endpoint = view_func.__name__

        old_func = self.view_functions.get(endpoint)

        # Avoid route overwriting
        if old_func is not None and old_func != view_func:
            raise AssertionError(
                "View function mapping is overwriting an "
                "existing endpoint function: %s" % endpoint
            )

        # Store the view function below the endpoint
        self.view_functions[endpoint] = view_func

        if options is None:
            # http://werkzeug.pocoo.org/docs/routing/#werkzeug.routing.Rule
            return self.url_map.add(self.rule_class(rule, endpoint=endpoint))

        return self.url_map.add(
            self.rule_class(rule, endpoint=endpoint, **options))

    def get_adapter(self, **options):
        """Return a werkzeug MapAdapter bound to the *current* request's
        host and scheme.

        Host and scheme are read from the thread-local request on every
        call rather than cached on the (shared, singleton) router, so
        concurrent requests on different virtual hosts or schemes cannot
        clobber each other's URL generation.

        default options:
        (script_name=None, subdomain=None, url_scheme='http',
         default_method='GET', path_info=None, query_args=None)
        see the werkzeug Map.bind documentation.
        """
        request = getRequest()
        actual_url = request.get("ACTUAL_URL", "") if request else ""
        parts = urlsplit(actual_url)
        # Preserve the request scheme so force_external URLs are https
        # behind TLS instead of always http. Callers may still override.
        options.setdefault("url_scheme", parts.scheme or "http")
        return self.url_map.bind(parts.netloc, **options)

    def resolve(self, request, path):
        """Resolve the path+method to an (endpoint, values) pair.

        Returns None when no rule matches the path (so the caller can
        try the next router). Raises MethodNotAllowedError when the path
        matches but the HTTP method does not, so the client gets a 405
        rather than a misleading 404.
        """
        method = request.environ.get("REQUEST_METHOD", "GET")
        logger.debug("router.resolve: method=%s path=%s", method, path)
        adapter = self.get_adapter(path_info=path)
        try:
            return adapter.match(method=method)
        except WzNotFound:
            return None
        except WzMethodNotAllowed as exc:
            allowed = ", ".join(sorted(exc.valid_methods or []))
            raise MethodNotAllowedError(
                "Method {} not allowed on {}. Allowed: {}".format(
                    method, path, allowed or "(none)"))

    def execute(self, context, request, endpoint, values):
        """Call the view function registered for the given endpoint."""
        return self.view_functions[endpoint](context, request, **values)

    def match(self, context, request, path):
        """Backward-compatible matcher.

        Returns (endpoint, values) or raises NotFoundError when no rule
        matches / MethodNotAllowedError when the method is wrong. New
        callers should prefer `resolve`, which returns None on no-match
        instead of raising, so a single werkzeug match serves both the
        "does this router handle it?" question and the dispatch.
        """
        resolved = self.resolve(request, path)
        if resolved is None:
            raise NotFoundError("No route matches {}".format(path))
        return resolved

    def url_for(self, endpoint, **options):
        """ get the url for the endpoint

        default options:
        (values=None, method=None, force_external=False, append_unknown=True)
        see the werkzeug MapAdapter.build documentation.
        """

        # XXX: this is all a little bit hacky, especially when it comes
        # to virtual hosting.

        request = getRequest()
        spp = request.physicalPathFromURL(request.getURL())

        # find the API view root
        path = []
        for el in spp:
            path.append(el)
            if el == "API" or el == "@@API":
                break

        virt_path = request.physicalPathToVirtualPath(path)
        script_name = request.physicalPathToURL(virt_path, relative=1)

        adapter = self.get_adapter(script_name=script_name)
        return adapter.build(endpoint, **options)

    def __call__(self, context, request, path):
        """ calls the matching view function for the given path
        """
        logger.debug("router.__call__: path=%s", path)

        endpoint, values = self.match(context, request, path)
        return self.execute(context, request, endpoint, values)


DefaultRouter = Router()


def DefaultRouterFactory():
    logger.debug("DefaultRouterFactory")
    return DefaultRouter


# -----------------------------------------------------------------------------
# Exposed Router API
# -----------------------------------------------------------------------------


def add_route(rule, endpoint=None, **kw):
    """ wrapper to add an url rule

    Example:

    >>> from plone.jsonapi import router
    >>> @router.add_route("/hello/<string:name>", "hello", methods=["GET"])
    ... def hello(context, request, name="world"):
    ...     return dict(hello=name)
    """

    def wrapper(f):
        DefaultRouter.add_url_rule(
            rule, endpoint=endpoint, view_func=f, options=kw)
        return f

    return wrapper


def url_for(endpoint, **options):
    """ method to retrieve the API URL of an endpoint

    Example::

    >>> from plone.jsonapi import router
    >>> router.url_for("hello", values={"name": "jsonapi"}, force_external=True)
    """
    return DefaultRouter.url_for(endpoint, **options)
