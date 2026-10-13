# Express engineering baseline

**Trigger:** The target package declares or has parsed evidence for `express`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Register parsing/authentication/routes/not-found/error middleware in deliberate order. Validate request values before services and propagate async failures using the installed Express major contract.

- Keep per-request state isolated and avoid blocking the Node event loop. Configure proxy trust from the actual topology, bound payloads/timeouts and own connection/worker shutdown.

- Test middleware ordering, rejected handlers, response completion and graceful shutdown. Production logging, caching and process management follow the project deployment rather than example defaults.

Source: [Official reference](https://expressjs.com/en/advanced/best-practice-performance/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
