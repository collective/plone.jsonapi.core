# plone.jsonapi.core

An extensible Plone JSON API framework.

- **Author:** Ramon Bartl
- **Version:** 0.8.0


## Abstract

`plone.jsonapi.core` lets you expose content and functionality of a Plone
site as JSON, by registering routes that are dispatched to endpoint
functions.


## Features

- A Werkzeug-based router that dispatches `@@API` requests to endpoint
  functions or `IRouteProvider` utilities.
- All standard HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`)
  reach the API view; the framework clears Zope's WebDAV handling for
  API requests so the non-GET/POST verbs are routed instead of being
  intercepted.
- A typed exception hierarchy (`APIError` and subclasses such as
  `NotFoundError`, `UnauthorizedError`, `ForbiddenError`,
  `ValidationError`) mapped to the correct HTTP status codes.
- A swappable error handler (`IErrorHandler` utility) that renders a
  consistent JSON error envelope without leaking tracebacks.
- Proper `404` / `405` responses for unknown routes and methods.
- Opt-in CORS support (`add_cors_headers` / the `@cors` decorator).
- A thread-safe router: per-request host/scheme are read from the
  current request, never cached on the shared router.


## Architecture and scope

`plone.jsonapi.core` is intentionally a **thin routing layer**, not a
full REST framework. Understand what it does and — just as importantly
— what it deliberately leaves to you:

- **It bypasses object traversal.** The `@@API` browser view swallows
  the whole sub-path and hands it to a URL router. Routes therefore
  have stable, flat URLs that are independent of where content lives in
  the site, and an endpoint is free to answer straight from the catalog
  without waking up content objects — which is fast, but means the
  request never acquires a content object's security context.

- **It does not serialize for you.** An endpoint returns a plain
  `dict` (or list); turning content into that structure is the
  endpoint's job. There is no serializer/deserializer adapter layer.

- **It does not enforce permissions.** This is the most important thing
  to know. The `@@API` view is published with the `zope2.View`
  permission, which Anonymous holds at the site root, and because the
  request bypasses traversal there is no per-object security check.
  **Every route implementation is responsible for authorizing the
  request itself** (see [Permissions](#permissions)). A route that
  forgets to check a permission is reachable by anonymous callers.
  Treat "check the permission first" as the default for every
  non-public endpoint.

If you need content-negotiated serialization, HATEOAS, or
traversal-based per-object security out of the box, `plone.restapi` is
the heavier but batteries-included alternative. `plone.jsonapi.core` is
for when you want a small, explicit router and full control over each
endpoint.


## Motivation

This project was born in 2012, out of the need for a data source to
build a network-based iOS application — or more precisely, wanting to
learn iOS programming and knit a JSON API for it.

Providing a routing mechanism for Plone that dispatches the request
after the `ZPublisher` has done its job is a little unusual, but it
worked, and so it stuck.


## HTTP methods

All standard HTTP methods reach the API view: `GET`, `POST`, `PUT`,
`PATCH` and `DELETE`. Earlier versions were limited to `GET` and `POST`
because Zope's publisher diverted the other verbs to its WebDAV
machinery before they reached the `@@API` view; the framework now
clears that handling for API requests so every verb is routed normally.

Because the API view is published with the `zope2.View` permission, you
must programmatically check for the correct permissions on your custom
routes (see [Permissions](#permissions)).


## Compatibility

`plone.jsonapi.core` works with [Plone](https://plone.org) 5.2 on
Python 2.7 and Python 3.8.


## Installation

The official release is on PyPI, so you simply include
`plone.jsonapi.core` in your buildout config:

```ini
[buildout]
...

[instance]
...
eggs =
    ...
    plone.jsonapi.core
```


## API URL

After installation, the API view is available as a browser view on your
Plone site with the name `@@API`, for example
`http://localhost:8080/Plone/@@API`.


## API framework

The main work is done in the `plone.jsonapi.core.browser.api` module.
It dispatches the incoming request to an endpoint function.


## The API router

The `Router` manages and maintains API routes to endpoints.

Routes are defined by so-called "route providers". A route provider is
either a named utility that implements the `IRouteProvider` interface,
or simply a function registered via the `add_route` decorator.


### Basic example

The most basic route provider is a decorated function:

```python
from plone.jsonapi.core import router


@router.add_route("/hello/<string:name>", "hello", methods=["GET"])
def hello(context, request, name="world"):
    return {"hello": name}
```

The `context` and `request` are passed in from the `@@API` view and can
be used to query Plone tools, utilities or adapters.


### A more complex example

Here we add a route provider named `my_routes`, registered as a named
utility. Add a `routes.py` module to your package:

```python
from zope.interface import implementer
from plone.jsonapi.core.interfaces import IRouteProvider


@implementer(IRouteProvider)
class ExampleRoutes(object):

    def initialize(self, context, request):
        """Called by the JSON API framework."""
        pass

    @property
    def routes(self):
        return (
            ("/hello/<string:name>", "hello", self.json_hello,
             dict(methods=["GET"])),
        )

    def json_hello(self, context, request, name="world"):
        return {"hello": name}
```

Register the utility in your `configure.zcml`:

```xml
<!-- Extension point for custom routes -->
<utility
    name="my_routes"
    provides="plone.jsonapi.core.interfaces.IRouteProvider"
    factory=".routes.ExampleRoutes" />
```

Each route provider is initialized with the `context` and the `request`
in an `initialize` method called by the API framework. The provider
must expose a `routes` property (or method) returning a tuple of route
definitions. Each definition is the URL rule (`/hello/<string:name>`),
an endpoint name (`hello`), the callable to invoke on a match
(`self.json_hello`), and a dictionary of routing `options`.

The `options` dictionary is passed straight to the
[Werkzeug](https://werkzeug.palletsprojects.com) routing machinery; see
its [rule format](https://werkzeug.palletsprojects.com/routing/#rule-format).

> `plone.jsonapi.core` ships a default router built on Werkzeug. You can
> plug in a different one via the ZCA by registering a utility that
> implements the `IRouter` interface.

To test the route, browse to:

```
http://localhost:8080/Plone/@@API/hello/JSON%20Plone%20API
```

```json
{
    "_runtime": 0.00025200843811035156,
    "hello": "JSON Plone API"
}
```


## Building URLs

When designing a RESTful JSON API you often want to include URLs to your
resources. The `plone.jsonapi.core.router` module provides a `url_for`
helper:

```python
from plone.jsonapi.core import router


@router.add_route("/hello/<string:name>", "hello", methods=["GET"])
def hello(context, request, name="world"):
    return {
        "url": router.url_for(
            "hello", values={"name": name}, force_external=True),
        "hello": name,
    }
```

It builds URLs using the `build` method of Werkzeug's `MapAdapter`; see
the [MapAdapter.build](https://werkzeug.palletsprojects.com/routing/#werkzeug.routing.MapAdapter.build)
docs. The resulting JSON:

```json
{
    "url": "http://localhost:8080/Plone/@@API/hello/world",
    "_runtime": 0.002997875213623047,
    "hello": "world"
}
```


## Permissions

The framework does **not** authorize requests for you (see
[Architecture and scope](#architecture-and-scope)). Every non-public
route must check its own permission. For example, to restrict the
`hello` route:

```python
from AccessControl import getSecurityManager
from AccessControl import Unauthorized

from plone.jsonapi.core import router


@router.add_route("/hello/<string:name>", "hello", methods=["GET"])
def hello(context, request, name="world"):

    if not getSecurityManager().checkPermission("ViewHelloAPI", context):
        raise Unauthorized("You don't have the 'ViewHelloAPI' permission")

    return {
        "url": router.url_for(
            "hello", values={"name": name}, force_external=True),
        "hello": name,
    }
```

Raising `Unauthorized` (or one of the typed errors from
`plone.jsonapi.core.browser.exceptions`, such as `ForbiddenError`) is
turned into a JSON error envelope with the matching HTTP status:

```json
{
    "_runtime": 0.0021250247955322266,
    "success": false,
    "message": "You don't have the 'ViewHelloAPI' permission",
    "type": "Unauthorized"
}
```
