Changelog
=========

0.4 - unreleased
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
