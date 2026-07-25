# -*- coding: utf-8 -*-

import logging
import os
import time

import dicttoxml
import simplejson as json
from ZPublisher.Iterators import filestream_iterator
from zope.component import queryUtility

from .exceptions import APIError  # noqa: F401  re-exported
from .helpers import error
from .interfaces import IErrorHandler

__author__ = "Ramon Bartl <rb@ridingbytes.com>"
__docformat__ = "plaintext"

logger = logging.getLogger("plone.jsonapi.core.decorators")


def handle_errors(f):
    """JSON error handler for API routes.

    Delegates envelope construction to the IErrorHandler utility so
    consumers can plug their own without monkey-patching. The default
    utility (`default_error_handler`) logs the full traceback and
    returns `{success: False, message: str(exc), type: <class>}` with
    the appropriate HTTP status set on the response.
    """

    def decorator(instance, *args, **kwargs):
        try:
            return f(instance, *args, **kwargs)
        except Exception as exc:
            request = getattr(instance, "request", None)
            handler = queryUtility(IErrorHandler)
            if handler is None:
                handler = default_error_handler
            return handler(exc, request)

    return decorator


def default_error_handler(exc, request):
    """Default IErrorHandler implementation.

    Logs the full traceback server-side (never in the response body)
    and returns an envelope carrying:

    - `success`: False (kept for backward compatibility with
      pre-typed-exceptions clients)
    - `message`: `str(exc)` - the exception's human-facing message,
      no stack frames
    - `type`: the exception's class name so clients can distinguish
      error kinds without parsing free-form text (CWE-209 fix: the
      previous implementation put `traceback.format_exc()` in
      `message`, exposing file paths and code structure).

    HTTP response status comes from `exc.status` when the exception
    is an APIError (or any object exposing a `status` int); 500
    otherwise. Bare `Exception` implies nothing about intent, so 500
    is the correct default.
    """
    logger.exception("JSON API error: %s", exc)

    status = getattr(exc, "status", None)
    if not isinstance(status, int):
        status = 500

    if request is not None:
        response = getattr(request, "response", None)
        if response is not None:
            response.setStatus(status)

    return error(str(exc), type=type(exc).__name__)


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
        request = getattr(instance, "request", None)
        request.response.setHeader("Content-Type", "application/json")
        result = func(*args, **kwargs)
        return json.dumps(result)

    return decorator


def returns_binary_stream(func):
    """ returns a binary file stream
    """

    def decorator(*args, **kwargs):
        instance = args[0]
        request = getattr(instance, "request", None)
        request.response.setHeader("Content-Type", "application/zip")
        zip_out = func(*args, **kwargs)
        request.response.setHeader(
            "Content-Length", str(os.path.getsize(zip_out)))
        return filestream_iterator(zip_out)

    return decorator


def returns_xml(func):
    """ returns xml
    """

    def decorator(*args, **kwargs):
        instance = args[0]
        request = getattr(instance, "request", None)
        request.response.setHeader("Content-Type", "application/xml")
        result = func(*args, **kwargs)
        return dicttoxml.dicttoxml(result)

    return decorator
