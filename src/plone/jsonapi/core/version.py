# -*- coding: utf-8 -*-

from .browser import router

import pkg_resources


__author__ = "Ramon Bartl <rb@ridingbytes.com>"
__docformat__ = "plaintext"


def version():
    dist = pkg_resources.get_distribution("plone.jsonapi.core")
    return dist.version


__version__ = version()


@router.add_route("/version", "apiversion", methods=["GET"])
def apiversion(context, request):
    return {
        "url": router.url_for("apiversion", force_external=True),
        "version": __version__,
    }
