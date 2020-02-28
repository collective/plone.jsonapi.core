# -*- coding: utf-8 -*-

from zope import interface


__author__ = "Ramon Bartl <ramon.bartl@googlemail.com>"
__docformat__ = "plaintext"


class IAPI(interface.Interface):
    """ The API View
    """


class IRouter(interface.Interface):
    """ The API Router
    """

    def __call__(self, context, request, path):
        """ gets called with the resource path
        """

    def add_url_rule(self, rule, endpoint=None, view_func=None, options=None):
        """ adds an url rule to the routing mechanism
        """


class IRouteProvider(interface.Interface):
    """ utlitiy which provides an api route
    """

    def initialize(context, request):
        """ get's called by the API Framework
        """

    def routes(self):
        """ needs to return a tuple of tuples containing
            rule, endpoint, view_func and additional options
        """
