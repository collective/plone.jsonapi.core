Changelog
=========


0.6 - 2017-01-10
----------------

- Supports XML response.
  Use the request parameter `asxml=1` or set the request `Accept` header to
  `application/xml`

- https://github.com/collective/plone.jsonapi.core/issues/21
  Support file streams.
  Use the request parameter `asbinary=1` or set the request `Accept` header to
  `application/zip`

- https://github.com/collective/plone.jsonapi.core/issues/22
  Do not store the request on the router upon initialization

- https://github.com/collective/plone.jsonapi.core/issues/18
  Handle None values

- https://github.com/collective/plone.jsonapi.core/issues/17
  Print out Traceback's to the console and not back to the client


0.5 - 2015-07-09
----------------

- https://github.com/collective/plone.jsonapi.core/pull/14
  use ``urlsplit(request.get("ACTUAL_URL", "")).netloc`` to get the hostname

- added more tests

- changed info to debug logging to reduce verbosity

- smoe minor code cleanup


0.4 - 2014-03-04
----------------

- https://github.com/ramonski/plone.jsonapi.core/issues/10
  add the traceback to the response when an error occurs
- https://github.com/ramonski/plone.jsonapi.core/issues/7
  started with doctests


0.3 - 2014-01-23
----------------

- renamed package to `plone.jsonapi.core` due to namespace conflicts with
  `plone.jsonapi.routes`
- removed default plone route configuration.
- added `version` route
- changed the `url_for` method of the router to provide correct urls for
  virtual hosting.


0.2 - 2013-08-11
----------------

- Router implementation updated to support decorated functions as route
  providers.

- url_for functionality implemented

- documentation changed


0.1 - unreleased
----------------

- initial start of development

.. vim: set ft=rst ts=4 sw=4 expandtab tw=78 :
