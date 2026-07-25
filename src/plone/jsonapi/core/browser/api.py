# -*- coding: utf-8 -*-

from .decorators import handle_errors
from .decorators import returns_binary_stream
from .decorators import returns_json
from .decorators import returns_xml
from .decorators import runtime
from .exceptions import APIError
from .exceptions import NotFoundError
from .interfaces import IAPI
from .interfaces import IRouter
from Products.Five import BrowserView
from zope import component
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging


__author__ = "Ramon Bartl <ramon.bartl@googlemail.com>"
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

        Router.match raises NotFoundError / MethodNotAllowedError when
        the path or method does not resolve; earlier versions returned
        None silently, which surfaced as an empty 200 response. Try
        each registered router in turn; the first successful match
        wins. Only the last router's error is reraised, so ordering
        matters when multiple routers are registered.
        """
        path = "/".join(self.traverse_subpath)
        logger.debug("Dispatching path: '%s'", path)

        last_error = None
        for name, router in component.getUtilitiesFor(IRouter):
            router.initialize(self.context, self.request)
            try:
                match = router.match(self.context, self.request, path)
            except APIError as exc:
                last_error = exc
                continue
            if match:
                logger.debug("Router '%r' will handle the request", router)
                return router(self.context, self.request, path)

        # No router matched: reraise the most-recent match failure, or
        # a bare NotFoundError if none of the routers even threw.
        if last_error is not None:
            raise last_error
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
        if self.request.form.get("asbinary", False) or accept == "application/zip":
            return self.to_binary_stream()
        if self.request.form.get("asxml", False) or accept == "application/xml":
            return self.to_xml()
        # return JSON per default
        return self.to_json()
