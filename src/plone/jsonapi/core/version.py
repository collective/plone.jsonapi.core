# -*- coding: utf-8 -*-

import pkg_resources
from browser import router

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


def version():
    dist = pkg_resources.get_distribution("plone.jsonapi.core")
    return dist.version


__version__ = version()
__build__ = 43
__date__ = '2015-07-09'


@router.add_route("/version", "apiversion", methods=["GET"])
def apiversion(context, request):
    return {
        "url":     router.url_for("apiversion", force_external=True),
        "version": __version__,
        "build":   __build__,
        "date":    __date__,
    }
