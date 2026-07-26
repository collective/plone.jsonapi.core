Plone JSONAPI Integration Tests
===============================

With `plone.jsonapi.core` enabled, it is simple to expose functions within
Plone. You only have to wrap your function around the `@router.add_route`
decorator.

The following doctest will demonstrate how the framework works and how to
register new routes.


Some needed imports::

    >>> import json
    >>> from plone.jsonapi.core import router
    >>> from plone.jsonapi.core.version import version

Prepare the browser::

    >>> browser = self.getBrowser()

Remember some URLs::

    >>> portal = self.getPortal()
    >>> portal_url = portal.absolute_url()
    >>> api_url = portal_url + "/@@API"
    >>> version_url = api_url + "/version"

Check if the version URL returns the right version::

    >>> browser.open(version_url)
    >>> dct = json.loads(browser.contents)
    >>> dct["url"] == version_url
    True
    >>> dct["version"] == version()
    True

Testing the framework -- lets add a new GET route::

    >>> @router.add_route("/hello/<string:name>", "hello", methods=["GET"])
    ... def hello(context, request, name="world"):
    ...     return dict(hello=name)

    >>> browser.open(api_url + "/hello/world")
    >>> print(json.loads(browser.contents).get("hello"))
    world


Testing the framework -- lets add a new POST route::

    >>> @router.add_route("/hello", "hello_post", methods=["POST"])
    ... def hello_post(context, request):
    ...     return {"hello": "post"}

    >>> browser.post(api_url + "/hello", "")
    >>> print(json.loads(browser.contents).get("hello"))
    post


Check what happens when a route throws an error. The error handler
turns it into a JSON envelope with the matching HTTP status (500 for a
bare exception) instead of leaking a traceback::

    >>> @router.add_route("/fail", "fail", methods=["GET"])
    ... def fail(context, request):
    ...     raise RuntimeError("This failed badly")

    >>> resp = browser.testapp.get(api_url + "/fail", expect_errors=True)
    >>> resp.status_int
    500
    >>> print(json.loads(resp.body).get("message"))
    This failed badly

The envelope also carries the exception class name in `type`::

    >>> print(json.loads(resp.body).get("type"))
    RuntimeError


Testing the framework -- PUT, PATCH and DELETE routes::

    >>> @router.add_route("/verb", "verb",
    ...                   methods=["PUT", "PATCH", "DELETE"])
    ... def verb(context, request):
    ...     return {"method": request.get("REQUEST_METHOD")}

    >>> resp = browser.testapp.put(api_url + "/verb", expect_errors=True)
    >>> resp.status_int
    200
    >>> print(json.loads(resp.body).get("method"))
    PUT

    >>> resp = browser.testapp.patch(api_url + "/verb", expect_errors=True)
    >>> print(json.loads(resp.body).get("method"))
    PATCH

    >>> resp = browser.testapp.delete(api_url + "/verb", expect_errors=True)
    >>> print(json.loads(resp.body).get("method"))
    DELETE


An unknown route returns a 404::

    >>> resp = browser.testapp.get(api_url + "/no/such/route",
    ...                            expect_errors=True)
    >>> resp.status_int
    404


A wrong method on a known route returns a 405::

    >>> resp = browser.testapp.post(api_url + "/verb", "", expect_errors=True)
    >>> resp.status_int
    405


Test XML::

    >>> @router.add_route("/xml", "xml", methods=["GET"])
    ... def xml(context, request):
    ...     return {"type": "xml"}
    >>> browser.open(api_url + "/xml?asxml=1")
    >>> print(browser.contents.decode("utf-8"))
    <?xml version="1.0" encoding="UTF-8" ?><root><type type="str">xml</type></root>


Test Binary Stream::

    >>> @router.add_route("/data", "data", methods=["GET"])
    ... def data(context, request):
    ...     return self.get_testfile_path()
    >>> browser.open(api_url + "/data?asbinary=1")
    >>> browser.contents[:5] == b"%PDF-"
    True
