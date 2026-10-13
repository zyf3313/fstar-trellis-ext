# Flask engineering baseline

**Trigger:** The target package declares or has parsed evidence for `flask`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Use application factories/blueprints and initialize extensions under the actual application owner. Keep request/app-context objects inside their context and pass explicit values to background work.

- Validate request/session inputs, map domain failures consistently and close transaction/resources on teardown. Account for concurrent worker processes instead of relying on mutable module globals.

- Test factory isolation, request errors and teardown through the configured test client. Verify WSGI server/proxy/trusted-host settings against the installed release; development serving is not deployment acceptance.

Source: [Official reference](https://flask.palletsprojects.com/en/stable/deploying/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
