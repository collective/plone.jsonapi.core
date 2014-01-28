Integration Tests
-----------------

Some needed imports::

    >>> import simplejson as json
    >>> from plone.jsonapi.core import router
    >>> from plone.jsonapi.core.version import version

Prepare the browser::

    >>> browser = self.getBrowser()

Remember some URLs::

    >>> portal_url = self.portal.absolute_url()
    >>> api_url = portal_url + "/@@API"
    >>> version_url = api_url + "/version"

Check if the version URL returns the right version::

    >>> browser.open(version_url)
    >>> browser.contents
    '{"url": "...", "_runtime": ..., "version": "..."}'

    >>> dct = json.loads(browser.contents)
    >>> dct["url"] == version_url
    True
    >>> dct["version"] == version()
    True

Testing the framework -- lets add a new route::

    >>> @router.add_route("/hello/<string:name>", "hello", methods=["GET"])
    ... def hello(context, request, name="world"):
    ...     return dict(hello=name)

    >>> browser.open(api_url + "/hello/world")
    >>> browser.contents
    '{"_runtime": ..., "hello": "world"}'

Check what happenss when a route throws an Error::

    >>> @router.add_route("/fail", "fail", methods=["GET"])
    ... def fail(context, request):
    ...     raise RuntimeError("This failed badly")

    >>> browser.open(api_url + "/fail")
    >>> browser.contents
    '{"_runtime": ..., "message": "This failed badly", "success": false, "error": "Traceback (most recent call last):..."}'

.. vim: set ft=rst ts=4 sw=4 expandtab :
