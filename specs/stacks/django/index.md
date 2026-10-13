# Django engineering baseline

**Trigger:** The target package declares or has parsed evidence for `django`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Own settings, URL routing, applications and migrations in their established modules. Validate input at forms/serializers/service boundaries; keep ORM querysets and transaction scope deliberate.

- Separate database commit from external side effects and verify concurrency/constraint behavior with the actual engine. Migration history and production settings must match the selected Django/Python release.

- Check DEBUG/hosts/secrets, static/media ownership and WSGI/ASGI deployment configuration. Run configured tests and deployment checks; the development server is not a production deployment validation.

Source: [Official reference](https://docs.djangoproject.com/en/6.0/howto/deployment/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
