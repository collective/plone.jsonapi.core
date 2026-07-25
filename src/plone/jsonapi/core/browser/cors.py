# -*- coding: utf-8 -*-

"""Cross-Origin Resource Sharing (CORS) helpers for the JSON API.

Browser-based clients on a different origin (SPA dashboards, static
sites embedding a widget, integration UIs, ...) cannot call the JSON
API without CORS response headers. This module exposes:

- `add_cors_headers(request, origin=None, allow_credentials=False,
  allow_methods=None, allow_headers=None, max_age=None)` -- pure
  helper that writes the standard Access-Control-* headers on the
  response.

- `@cors(...)` -- decorator for route view functions that installs
  the headers on every response and short-circuits OPTIONS preflight
  requests with a 200 empty body.

Callers pass an `origin` explicitly (or a callable that receives
the request and returns the allowed origin string, useful for
policy-driven allow-lists). No implicit `*` -- the caller has to
opt in.
"""

import logging

__author__ = "Ramon Bartl <rb@ridingbytes.com>"
__docformat__ = "plaintext"

logger = logging.getLogger("plone.jsonapi.core.cors")

DEFAULT_ALLOW_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
DEFAULT_ALLOW_HEADERS = (
    "Accept",
    "Authorization",
    "Content-Type",
    "X-Requested-With",
)


def _resolve_origin(origin, request):
    """Return the string to send back in Access-Control-Allow-Origin.

    Accepts a plain string (returned as-is), a callable that takes
    the request and returns a string, or None (no header emitted).
    """
    if origin is None:
        return None
    if callable(origin):
        return origin(request)
    return origin


def add_cors_headers(request, origin=None, allow_credentials=False,
                     allow_methods=None, allow_headers=None,
                     max_age=None):
    """Write CORS response headers for the current request.

    :param request: the Zope request whose response gets the headers
    :param origin: allowed origin string, or callable(request)->str.
        None means no header is written and the request is treated as
        same-origin.
    :param allow_credentials: whether to include
        Access-Control-Allow-Credentials: true. Note: browsers refuse
        credentialed requests when the origin header is "*".
    :param allow_methods: iterable of HTTP methods; defaults to the
        common REST set including OPTIONS.
    :param allow_headers: iterable of request header names the client
        may send; defaults to Accept, Authorization, Content-Type,
        X-Requested-With.
    :param max_age: seconds the browser may cache the preflight
        response; None means no header.
    """
    response = getattr(request, "response", None)
    if response is None:
        return

    resolved = _resolve_origin(origin, request)
    if resolved is None:
        return

    response.setHeader("Access-Control-Allow-Origin", resolved)
    # Vary: Origin lets caches key by origin so a cached response for
    # origin A is not served to origin B.
    response.setHeader("Vary", "Origin")

    if allow_credentials:
        if resolved == "*":
            # Browsers reject credentialed requests when origin is *.
            logger.warning(
                "CORS allow_credentials=True is incompatible with "
                "origin='*'; the browser will reject the response.")
        response.setHeader("Access-Control-Allow-Credentials", "true")

    methods = allow_methods or DEFAULT_ALLOW_METHODS
    response.setHeader(
        "Access-Control-Allow-Methods", ", ".join(methods))

    headers = allow_headers or DEFAULT_ALLOW_HEADERS
    response.setHeader(
        "Access-Control-Allow-Headers", ", ".join(headers))

    if max_age is not None:
        response.setHeader("Access-Control-Max-Age", str(int(max_age)))


def cors(origin=None, allow_credentials=False, allow_methods=None,
         allow_headers=None, max_age=None):
    """Decorator that adds CORS headers to a route response and
    short-circuits OPTIONS preflight requests.

    Usage::

        @add_route("/things", "things", methods=["GET", "POST"])
        @cors(origin="https://dashboard.example.com",
              allow_credentials=True)
        def things(context, request):
            return {"items": [...]}

    See `add_cors_headers` for the parameter meaning.
    """
    def wrap(func):
        def decorator(context, request, *args, **kwargs):
            add_cors_headers(
                request,
                origin=origin,
                allow_credentials=allow_credentials,
                allow_methods=allow_methods,
                allow_headers=allow_headers,
                max_age=max_age,
            )
            method = request.environ.get("REQUEST_METHOD", "GET").upper()
            if method == "OPTIONS":
                # Preflight: headers were just written; body is empty.
                return {}
            return func(context, request, *args, **kwargs)
        return decorator
    return wrap
