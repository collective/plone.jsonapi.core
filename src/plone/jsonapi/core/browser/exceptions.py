# -*- coding: utf-8 -*-

"""Typed exception classes for the JSON API framework.

Every JSON API consumer used to invent its own exception class, then
map it to the right HTTP status in an ad-hoc handler. The classes
here give the framework a single shared hierarchy so downstream code
(bika.lims.jsonapi, senaite.jsonapi, custom integrations) can just
`raise NotFoundError("...")` and have the framework surface the
correct status and a stable `type` field to clients.

`APIError` is the base class. Every subclass carries a default HTTP
status; callers can override it per instance with `status=`.
Backward compatibility: any `except APIError:` handler catches every
subclass.
"""

__author__ = "Ramon Bartl <rb@ridingbytes.com>"
__docformat__ = "plaintext"


class APIError(Exception):
    """Base class for every JSON API error.

    Carries an HTTP status and a human-facing message. The framework
    error handler uses `.status` to set the response status and
    `type(exc).__name__` to populate the envelope's `type` field.
    """
    status = 500

    def __init__(self, message, status=None):
        if status is not None:
            self.status = status
        self.message = message

    def __str__(self):
        return self.message


class BadRequestError(APIError):
    """400 - the request is malformed or missing required fields."""
    status = 400


class UnauthorizedError(APIError):
    """401 - the caller is not authenticated.

    Distinct from `ForbiddenError`: 401 means "log in and try again",
    403 means "you are logged in but you may not do this".
    """
    status = 401


class ForbiddenError(APIError):
    """403 - the caller is authenticated but lacks permission."""
    status = 403


class NotFoundError(APIError):
    """404 - the addressed resource does not exist."""
    status = 404


class MethodNotAllowedError(APIError):
    """405 - the resource does not accept this HTTP method."""
    status = 405


class ConflictError(APIError):
    """409 - the request conflicts with the current resource state."""
    status = 409


class ValidationError(APIError):
    """422 - the payload is well-formed but semantically invalid."""
    status = 422
