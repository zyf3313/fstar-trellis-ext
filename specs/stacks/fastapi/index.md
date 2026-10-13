# FastAPI engineering baseline

**Trigger:** The target package declares or has parsed evidence for `fastapi`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Keep route request/response models and validation failures consistent with the installed FastAPI/Pydantic release. Dependencies own authentication and resources; avoid duplicating application service rules inside routes.

- Put startup/shutdown resources under the actual lifespan mechanism. Use async endpoints for cooperative IO and keep blocking work off that event loop; review sync thread-pool limits and worker multiplicity.

- Test response serialization, dependency cleanup, cancellation and validation errors. Confirm proxy/root-path, process management and external readiness on the target deployment.

Source: [Official reference](https://fastapi.tiangolo.com/deployment/concepts/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
