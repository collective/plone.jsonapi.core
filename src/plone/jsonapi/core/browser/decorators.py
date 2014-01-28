# -*- coding: utf-8 -*-
#
# File: decorators.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import time
import logging
import traceback
import simplejson as json
from helpers import error

logger = logging.getLogger("plone.jsonapi")


def handle_errors(f):
    """ simple JSON error handler
    """

    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        # XXX we should create a custom Exception class
        except Exception, e:
            return error(str(e), error=str(traceback.format_exc()))
    return decorator


def runtime(func):
    """ simple runtime measurement of the called function
    """

    def decorator(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        result.update(dict(_runtime=end-start))
        return result

    return decorator


def returns_json(func):
    """ returns json output
    """

    def decorator(*args, **kwargs):
        instance = args[0]
        request = getattr(instance, 'request', None)
        request.response.setHeader("Content-Type", "application/json")
        result = func(*args, **kwargs)
        return json.dumps(result)

    return decorator


def supports_jsonp(func):
    """ suports jsonp output
    """

    def decorator(*args, **kwargs):
        instance = args[0]
        request = getattr(instance, 'request', None)

        c = request.form.get("c", None)
        if c is not None:
            return "%s(%s);" % (str(c), func(*args, **kwargs))
        return func(*args, **kwargs)

    return decorator

# vim: set ft=python ts=4 sw=4 expandtab :
