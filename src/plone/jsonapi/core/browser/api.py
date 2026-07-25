# -*- coding: utf-8 -*-

from .decorators import handle_errors
from .decorators import returns_binary_stream
from .decorators import returns_json
from .decorators import returns_xml
from .decorators import runtime
from .exceptions import MethodNotAllowedError
from .exceptions import NotFoundError
from .interfaces import IAPI
from .interfaces import IRouter
from Products.Five import BrowserView
from zope import component
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging


__author__ = "Ramon Bartl <rb@ridingbytes.com>"
__docformat__ = "plaintext"


logger = logging.getLogger("plone.jsonapi.core.api")


@implementer(IAPI, IPublishTraverse)
class API(BrowserView):
    """ JSON API Framework
    """

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
        """Dispatch the given subpath to the first matching router.

        Each router is asked to `resolve` the path with a single werkzeug
        match: it returns an (endpoint, values) pair when it handles the
        path, or None so the next router gets a turn. A resolved router
        executes the view immediately -- no second match. A
        MethodNotAllowedError (path matches, method doesn't) is deferred:
        another router might still fully handle the request, so it is
        only raised once every router has been tried. NotFoundError is
        raised when no router matched at all.
        """
        path = "/".join(self.traverse_subpath)
        logger.debug("Dispatching path: '%s'", path)

        method_not_allowed = None
        for name, router in component.getUtilitiesFor(IRouter):
            router.initialize(self.context, self.request)
            try:
                resolved = router.resolve(self.request, path)
            except MethodNotAllowedError as exc:
                # Remember it, but let another router try to serve the
                # method before giving up with a 405.
                method_not_allowed = exc
                continue
            if resolved is None:
                continue
            logger.debug("Router '%r' will handle the request", router)
            endpoint, values = resolved
            return router.execute(self.context, self.request, endpoint, values)

        if method_not_allowed is not None:
            raise method_not_allowed
        raise NotFoundError("No route matches {}".format(path))

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
        if (self.request.form.get("asbinary", False)
                or accept == "application/zip"):
            return self.to_binary_stream()
        if (self.request.form.get("asxml", False)
                or accept == "application/xml"):
            return self.to_xml()
        # return JSON per default
        return self.to_json()
