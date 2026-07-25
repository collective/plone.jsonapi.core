# -*- coding: utf-8 -*-

"""Let the JSON API receive PUT / PATCH / DELETE.

Zope decides very early in publishing -- in `BaseRequest.traverse`,
before the API view is ever reached -- whether a non-GET/POST request
is a WebDAV client, by reading `request.maybe_webdav_client`. When that
flag is set, ZPublisher may substitute a WebDAV `NullResource` at path
exhaustion, so the request never reaches the API view and PUT/PATCH/
DELETE effectively cannot be routed.

The flag is consumed before traversal, so it cannot be cleared from the
view itself. The only hook that runs early enough is an `IPubStart`
subscriber. We clear the flag for requests addressed to the API view,
identified by an `@@API` (or acquisition-form `API`) path segment, so
the router can dispatch these verbs. Genuine WebDAV requests to other
content are untouched -- the flag is only cleared for API URLs.

This mirrors the technique `plone.rest` uses for the same purpose.
"""

import logging

__author__ = "Ramon Bartl <rb@ridingbytes.com>"
__docformat__ = "plaintext"

logger = logging.getLogger("plone.jsonapi.core.webdav")

# Verbs ZPublisher would otherwise hand to the WebDAV machinery instead
# of the API view.
WEBDAV_VERBS = frozenset(["PUT", "PATCH", "DELETE"])

# Path segments that identify a request bound for the API view. The
# view is registered as @@API and reachable either explicitly (@@API)
# or via acquisition (API); this matches the same marker the router
# uses when building URLs.
API_SEGMENTS = frozenset(["@@API", "API"])


def is_api_request(path_info):
    """True if any path segment marks this as an API-view request."""
    segments = path_info.split("/")
    return bool(API_SEGMENTS.intersection(segments))


def allow_api_verbs(event):
    """IPubStart subscriber: clear maybe_webdav_client for API requests
    using PUT/PATCH/DELETE so they reach the API view.
    """
    request = event.request
    method = request.get("REQUEST_METHOD", "GET").upper()
    if method not in WEBDAV_VERBS:
        return
    path_info = request.get("PATH_INFO", "") or ""
    if is_api_request(path_info):
        logger.debug(
            "Clearing maybe_webdav_client for API %s %s", method, path_info)
        request.maybe_webdav_client = 0
