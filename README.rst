plone.jsonapi.core
==================

:Author: Ramon Bartl
:Version: 0.4dev

.. contents:: Table of Contents
   :depth: 2


Latest Build Status
-------------------

.. image:: https://api.travis-ci.org/ramonski/plone.jsonapi.core.png?branch=develop
    :target: https://travis-ci.org/ramonski/plone.jsonapi.core
    :alt: Build Status


Abstract
--------

An extensible Plone JSON API Framework


Introduction
------------

This Package allows Users to expose content information via JSON.


Motivation
----------

This project was born in 2012, out of the need for a data source to build a
network based iOS application. Or more precise, I wanted to learn iOS
programming and wanted to knit my own JSON API:)

I know, it is a little bit awkward to provide an own routing mechanism for
Plone which dipatches the request after the ``ZPublisher`` did its job, but it
worked and thus, I did it.


Limitations
-----------

Since the API comes after the ``ZPublisher``, it can only make use of ``HTTP
GET`` and ``HTTP POST`` methods. The other methods will never reach the API
View.

Be aware that the API View comes with the permission ``zope2.View``, so you need
to programmatically check for the correct permissions on your custom routes.

See: http://developer.plone.org/security/permission_lists.html


Compatibility
-------------

The plone.jsonapi.core_ should work with Plone_ 3 and 4.

.. note:: Users of Plone_ 3 should pin the versions of simplejson_ and Werkzeug_.

Example::

    [buildout]
    ...
    versions = versions

    [versions]
    ...
    simplejson = 2.0.9
    werkzeug = 0.7.2


Installation
------------

There official release is on pypi, so you have to simply include
plone.jsonapi.core_ to your buildout config.

Example::

    [buildout]
    ...

    [instance]
    ...
    eggs =
        ...
        plone.jsonapi.core


API URL
-------

After installation, the API View is available as a Browser View on your Plone
site with the name ``@@API``, for example ``http://localhost:8080/Plone/@@API``.


API Framework
-------------

The main work is done in the ``plone.jsonapi.core.browser.api`` module.  This
module dispatches the incoming request and dispatches it to an endpoint
function.


The API Router
--------------

The `Router` is responsible to manage and maintain API routes to endpoints.

Routes get defined by so called "Route Providers".

A route provider is either a named Utility class, which implements the
``IRouteProvider`` interface, or simply a function, which is registered
via the ``add_route`` decorator.


Basic Example
~~~~~~~~~~~~~

The most basic route provider is simply a decorated function::

    from plone.jsonapi.core import router

    @router.add_route("/hello/<string:name>", "hello", methods=["GET"])
    def hello(context, request, name="world"):
        return {"hello": name}

The passed in context and request gets passed of the ``@@API`` View.
It can be used to query Plone tools or other utilities or adapters.


A more complex Example
~~~~~~~~~~~~~~~~~~~~~~

In this Example, we're going to add a route provider named ``my_routes``.
This route provider gets registered as an named Utility_.

To do so, we add a module called ``routes.py`` to our package and add the
following code::

    from zope import interface
    from plone.jsonapi.core.interfaces import IRouteProvider

    class ExampleRoutes(object):
        interface.implements(IRouteProvider)


        def initialize(self, context, request):
            """ called by the json api framework"""
            pass

        @property
        def routes(self):
            return (
                ("/hello/<string:name>", "hello", self.json_hello, dict(methods=['GET'])),
            )

        def json_hello(self, context, request, name="world"):
            return {"hello": name}


To register the Utility_, we add this directive to the ``configure.zcml`` file::

    <!-- Extension point for custom routes -->
    <utility
        name="my_routes"
        provides="plone.jsonapi.core.interfaces.IRouteProvider"
        factory=".routes.ExampleRoutes" />

Or use grok::


    from five import grok

    ...

    grok.global_utility(ExampleRoutes, name="my_routes", direct=False)

Each route provider gets initialized with the ``context`` and the ``request`` in a
method called ``initialize``. This method gets called by the API framework.

Our route provider has to contain a ``routes`` property or method. It should
return a tuple of route definitions. Each route definition contains the url
rule (``/hello``), an endpoint name (``hello``), a method to be called when the url
matches (``self.json_hello``) and an additional dictionary with routing ``options``

The `options` dictionary get directly passed to the routing mechanism of Werkzeug_.
For details, see: http://werkzeug.pocoo.org/docs/routing/#rule-format

.. note:: plone.jsonapi.core_ comes with a default implementation of the router.
          This router uses the routing mechanism provided by Werkzeug_.
          It is possible to plug in a more sophisticated router by using the ZCA.
          Simply configure a class which implements the `IRouter` interface.

To test this route, browse to the ``/hello`` API url:

http://localhost:8080/Plone/@@API/hello/JSON%20Plone%20API


Result::

    {
        _runtime: 0.00025200843811035156,
        hello: "JSON Plone API"
    }


API URLs
--------

If you design your custom RESTful JSON API, you probably want to insert URLs to
your specified resources, e.g:

http://localhost:8080/Plone/@@API/news/news_items_1

The ``plone.jsonapi.core.router`` module comes with a ``url_for`` method.

So when you want to insert the URL for the defined ``hello`` endpoint, you simply
add it like this::

    from plone.jsonapi.core import router

    @router.add_route("/hello/<string:name>", "hello", methods=["GET"])
    def hello(context, request, name="world"):
        return {
            "url": router.url_for("hello", values={"name": name}, force_external=True),
            "hello": name,
        }

It builds the URLs using the ``build`` method of the MapAdapter of Werkzeug_.
For details, see http://werkzeug.pocoo.org/docs/routing/#werkzeug.routing.MapAdapter.build

The resulting JSON will look like this:

http://localhost:8080/Plone/@@API/hello/world

Result::

    {
        url: "http://localhost:8080/Plone/@@API/hello/world",
        runtime: 0.002997875213623047,
        hello: "world"
    }


Permissions
-----------

You have to handle the permissions for your routes manually.
so if you would like to restrict the permission of the ``hello`` route,
you have to do something like this::

    from AccessControl import getSecurityManager
    from AccessControl import Unauthorized

    from plone.jsonapi.core import router

    @router.add_route("/hello/<string:name>", "hello", methods=["GET"])
    def hello(context, request, name="world"):

        if not getSecurityManager().checkPermission("ViewHelloAPI", object):
            raise Unauthorized("You don't have the 'ViewHelloAPI' permission")

        return {
            "url": router.url_for("hello", values={"name": name}, force_external=True),
            "hello": name,
        }

Output::

    {
        runtime: 0.0021250247955322266,
        success: false,
        error: "You don't have the 'ViewHelloAPI' permission"
    }



License
-------

MIT - do what you want


.. _Plone: http://plone.org
.. _Dexterity: https://pypi.python.org/pypi/plone.dexterity
.. _Werkzeug: http://werkzeug.pocoo.org
.. _simplejson: https://pypi.python.org/pypi/simplejson
.. _plone.jsonapi.core: https://github.com/ramonski/plone.jsonapi.core
.. _mr.developer: https://pypi.python.org/pypi/mr.developer
.. _Utility: http://developer.plone.org/components/utilities.html

.. vim: set ft=rst ts=4 sw=4 expandtab :
