# -*- coding: utf-8 -*-
#
# File: __init__.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import pkg_resources

from browser import router
from browser import decorators


def version():
    dist = pkg_resources.get_distribution("plone.jsonapi")
    return dist.version


@router.add_route("/version", "apiversion", methods=["GET"])
def apiversion(context, request):
    return {
        "url": router.url_for("apiversion", force_external=True),
        "version": version()
    }

# vim: set ft=python ts=4 sw=4 expandtab :
