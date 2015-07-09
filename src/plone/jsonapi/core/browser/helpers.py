# -*- coding: utf-8 -*-

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


def error(message, **kw):
    result = {"success": False, "message": message}
    result.update(kw)
    return result


def success(message, **kw):
    result = {"success": True, "message": message}
    result.update(kw)
    return result
