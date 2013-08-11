# -*- coding: utf-8 -*-
#
# File: helpers.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

def error(message, **kw):
    result = {"success": False, "error": message}
    if kw:
        result.update(kw)
    return result

def success(message, **kw):
    result = {"success": True,
            "message": message}
    if kw:
        result.update(kw)

    return result

# vim: set ft=python ts=4 sw=4 expandtab :
