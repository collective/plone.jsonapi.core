# Proposal: declarative route permissions

- **Status:** draft
- **Affects:** `plone.jsonapi.core.browser.router`,
  `plone.jsonapi.core.browser.api`
- **Backward compatible:** yes (opt-in; default behavior unchanged)


## Problem

`plone.jsonapi.core` bypasses object traversal: the `@@API` view is
published with the weak `zope2.View` permission (which Anonymous holds
at the site root), and the request never acquires a content object's
security context. As a result the framework does **not** authorize
requests — each route is expected to check permissions itself:

```python
@router.add_route("/registry", "registry", methods=["GET"])
def registry(context, request):
    if not getSecurityManager().checkPermission("cmf.ManagePortal", context):
        raise Unauthorized("...")
    return read_registry()
```

This is a convention, not a guarantee. A route that forgets the check
is silently reachable by anonymous callers. Authorization bugs of
exactly this shape (an endpoint exposed without a permission check) are
the most common and most serious defect class for consumers of this
framework. Security should be something you *declare* and the framework
*enforces*, not something every author must remember to hand-write.


## Proposal

Add an optional `permission` to a route. When set, the router checks it
**before** invoking the endpoint and raises the appropriate typed error
if the caller is not allowed. When unset, behavior is exactly as today.

### API

Decorator form:

```python
@router.add_route(
    "/registry", "registry", methods=["GET"],
    permission="cmf.ManagePortal")
def registry(context, request):
    return read_registry()
```

`IRouteProvider` tuple form (the options dict already flows through):

```python
@property
def routes(self):
    return (
        ("/registry", "registry", self.registry,
         dict(methods=["GET"], permission="cmf.ManagePortal")),
    )
```

The value is a Zope permission name (a string), the same thing you
would pass to `getSecurityManager().checkPermission(...)`.

### Behavior

At dispatch time, once a route is resolved and before its endpoint is
called:

1. If the route declares no `permission`, call the endpoint (current
   behavior — fully backward compatible).
2. Otherwise check the permission on the dispatch context:
   - allowed -> call the endpoint;
   - denied and the caller is **anonymous** -> raise
     `UnauthorizedError` (HTTP 401, prompting authentication);
   - denied and the caller is **authenticated** -> raise
     `ForbiddenError` (HTTP 403).

Both errors are the existing typed exceptions, so they flow through
`handle_errors` / `IErrorHandler` into the normal JSON envelope with
the correct status — no new error plumbing.

The permission is checked against the **dispatch context** (the object
the `@@API` view was invoked on). This gives a reliable "you need
permission X to reach this endpoint at all" gate. Object-level checks
(e.g. against a specific object resolved by UID inside the endpoint)
remain the endpoint's responsibility; see *Future work*.


## Implementation sketch

`permission` is not a Werkzeug `Rule` keyword, so it must be popped from
the options before the rule is built and stored per endpoint, alongside
`view_functions`.

`router.py`:

```python
class Router(object):

    def __init__(self):
        self.rule_class = Rule
        self.view_functions = {}
        self.route_permissions = {}   # endpoint -> permission name
        self.url_map = Map()
        self.is_initialized = False

    def add_url_rule(self, rule, endpoint=None, view_func=None, options=None):
        if endpoint is None:
            endpoint = view_func.__name__
        options = dict(options or {})
        # Extract our own option before handing the rest to Werkzeug.
        permission = options.pop("permission", None)

        old_func = self.view_functions.get(endpoint)
        if old_func is not None and old_func != view_func:
            raise AssertionError(
                "View function mapping is overwriting an existing "
                "endpoint function: %s" % endpoint)

        self.view_functions[endpoint] = view_func
        self.route_permissions[endpoint] = permission
        return self.url_map.add(
            self.rule_class(rule, endpoint=endpoint, **options))

    def check_permission(self, endpoint, context):
        """Enforce the endpoint's declared permission, if any."""
        permission = self.route_permissions.get(endpoint)
        if permission is None:
            return
        if getSecurityManager().checkPermission(permission, context):
            return
        if getSecurityManager().getUser().getUserName() == "Anonymous User":
            raise UnauthorizedError(
                "Authentication required for '%s'" % endpoint)
        raise ForbiddenError(
            "You do not have the '%s' permission" % permission)

    def execute(self, context, request, endpoint, values):
        self.check_permission(endpoint, context)
        return self.view_functions[endpoint](context, request, **values)
```

(`getSecurityManager` from `AccessControl`; `UnauthorizedError` /
`ForbiddenError` from `plone.jsonapi.core.browser.exceptions`. The
anonymous test above is illustrative — `portal_membership.isAnonymousUser()`
or `zope.security` may be preferred in the real change.)

No change is needed in `api.py`: `dispatch()` already routes through
`Router.execute`, so the check applies to every dispatched request.


## Backward compatibility

- `permission` defaults to `None`; every existing route keeps working
  with no check, exactly as today.
- No signature breakage: `permission` is just another key in the
  `**options` / options dict.
- Existing manual `checkPermission` calls in endpoints continue to work
  and can be migrated to the declarative form incrementally.


## Migration path

1. Ship the feature (opt-in) as above.
2. Encourage every non-public route to declare a `permission`; migrate
   existing manual checks.
3. Optionally add a router **strict mode** (off by default) that logs a
   warning — or raises at registration time — for any route that
   declares no `permission`, so a project can enforce "every route must
   state its permission" once it has finished migrating.


## Future work (out of scope here)

- **Per-object permission context.** Allow a route to declare how to
  resolve the object the permission is checked against (e.g. a callable
  `permission_context=lambda context, request, **values: resolve(values["uid"])`),
  so object-level authorization can also be declarative.
- **Multiple permissions / roles.** Support a sequence (all-of / any-of)
  if a route needs more than one permission.


## Alternatives considered

- **Keep it a convention (status quo).** Rejected: it has repeatedly
  produced anonymously-reachable endpoints; the framework should make
  the safe path the default path.
- **Register endpoints as ZCA views with a real permission** (the
  `plone.rest` model). This is the most Zope-idiomatic answer and gets
  traversal-based security for free, but it is a much larger change that
  abandons the flat-URL / catalog-first model this package is built
  around. The declarative option above keeps that model while closing
  the security gap.
