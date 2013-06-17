# -*- coding: utf-8 -*-
#
# File: router.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

from werkzeug.routing import Map, Rule
from Acquisition import aq_inner


class Router(object):
    """ Plone API Router Tool
    """

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request

    @property
    def url_map(self):
        return Map([
            Rule('/contents', endpoint='contents'),
            Rule('/contents/<string:content>', endpoint='contents'),
            Rule('/query', endpoint='query'),
            Rule('/version', endpoint='version'),
            ])

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

# vim: set ft=python ts=4 sw=4 expandtab :
