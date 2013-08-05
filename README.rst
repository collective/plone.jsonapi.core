plone.jsonapi
=============

:Author: Ramon Bartl
:Version: 0.2


Abstract
--------

An extensible Plone JSON API Framework


Introduction
------------

This Package allows Users to expose content information via JSON.


Compatibility
-------------

The plone.jsonapi_ should work with Plone_ 3 and 4.
It should also work with Dexterity_ content types.


Installation
------------

There is currently no "official" release on pypi, so you have to use
`mr.developer` to include plone.jsonapi_ to your buildout config.

Example::

    [buildout]

    extensions =
        mr.developer

    auto-checkout = *

    [sources]
    plone.jsonapi = git git://github.com/ramonski/plone.jsonapi.git

    [instance]
    ...
    eggs =
        ...
        plone.jsonapi


API URL
-------

After installation, the API View is available on your Plone root with the
name ``@@API``, for example ``http://localhost:8080/Plone/@@API``


Quickstart
----------

The framework comes with a default implementation for Plone content types.
The resource name is ``contents`` and can be accessed here:

http://localhost:8080/Plone/@@API/contents


API Framework
-------------

The main work is done in the ``plone.jsonapi.api`` module.  This module
dispatches the incoming request and dispatches it to an endpoint function.


Adding Routes
-------------

Routes get defined by so called "route providers". These are named utilities
which implement the ``IRouteProvider`` interface.

Example
~~~~~~~

In this Example, we're going to add a simple route provider named ``my_routes``.
To do so, we add a module called ``routes.py`` to our package and add the
following code::

    from zope import interface
    from plone.jsonapi.interfaces import IRouteProvider

    class ExampleRoutes(object):
        interface.implements(IRouteProvider)


        def initialize(self, context, request):
            """ called by the json api framework"""
            pass

        @property
        def routes(self):
            return (
                ("/hello/<string:name>", "hello", self.json_hello, dict(methods=['GET']))
            )

        def json_hello(self, name="world"):
            return {"hello": name}


To register the utility, we add this directive to the ``configure.zcml`` file::

    <!-- Extension point for custom routes -->
    <utility
        name="my_routes"
        provides="plone.jsonapi.interfaces.IRouteProvider"
        factory=".routes.ExampleRoutes" />

Each route provider gets initialized with the ``context`` and the ``request`` in a
method called ``initialize``. This method gets called by the API framework.

Our route provider has to contain a ``routes`` property or method. It should
return a tuple of route definitions. Each route definition contains the url
rule (``/hello``), an endpoint name (``hello``), a method to be called when the url
matches (``self.json_hello``) and an additional dictionary with routing ``options``

The `options` dictionary get directly passed to the routing mechanism of Werkzeug_.
For details, see: http://werkzeug.pocoo.org/docs/routing/#rule-format

.. note:: plone.jsonapi_ comes with a default implementation of the router.
          This router uses the routing mechanism provided by Werkzeug_.
          It is possible to plug in a more sophisticated router by using the ZCA.
          Simply configure a class which implements the `IRouter` interface.

To test this route, browse to the ``/hello`` API url:

http://localhost:8080/@@API/hello/JSON%20Plone%20API


Result::

    {
        runtime: 0.00025200843811035156,
        hello: "JSON Plone API"
    }


Advanced configuration
----------------------

See the ``plone.jsonapi.routes`` module for advanced configuration.
This module implements a simple RESTful API for Plone content type
for the resource `contents`.

It uses a special Plone_ catalog helper (``plone.jsonapi.catalog``) for
searching content and building unique URLs using the UID of the found contents.


.. _Plone: http://plone.org
.. _Dexterity: https://pypi.python.org/pypi/plone.dexterity
.. _Werkzeug: http://werkzeug.pocoo.org
.. _plone.jsonapi: https://github.com/ramonski/plone.jsonapi
.. _mr.developer: https://pypi.python.org/pypi/mr.developer

.. vim: set ft=rst ts=4 sw=4 expandtab :
