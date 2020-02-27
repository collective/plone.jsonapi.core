# -*- coding: utf-8 -*-

from helpers import error
from ZPublisher.Iterators import filestream_iterator

import dicttoxml
import os
import simplejson as json
import time
import traceback
import types


__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


def handle_errors(f):
    """ simple JSON error handler
    """

    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        # XXX we should create a custom Exception class
        except Exception as e:
            # Print out the exception to the console
            traceback.print_exc()
            return error(str(e))

    return decorator


def runtime(func):
    """ simple runtime measurement of the called function
    """

    def decorator(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        if not isinstance(result, dict):
            result = error("Route providers must return a dictionary.")
        result.update(dict(_runtime=end - start))
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


def returns_binary_stream(func):
    """ returns a binary file stream
    """

    def decorator(*args, **kwargs):
        instance = args[0]
        request = getattr(instance, 'request', None)
        request.response.setHeader('Content-Type', 'application/zip')
        zip_out = func(*args, **kwargs)
        request.response.setHeader('Content-Length', str(os.path.getsize(zip_out)))
        return filestream_iterator(zip_out)

    return decorator


def returns_xml(func):
    """ returns xml
    """

    def decorator(*args, **kwargs):
        instance = args[0]
        request = getattr(instance, 'request', None)
        request.response.setHeader('Content-Type', 'application/xml')
        result = func(*args, **kwargs)
        return dicttoxml.dicttoxml(result)

    return decorator
