# Docker engineering baseline

**Trigger:** The target package declares or has parsed evidence for `docker`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Pin the project-selected base images/dependencies and minimize build context with its ignore rules. Separate build secrets from image layers and run with the application permissions actually needed.

- Own volumes, configuration and networks explicitly; readiness/health and shutdown behavior must follow application dependencies. Container creation or exposed ports do not prove service readiness or durable data safety.

- Validate selected image/Compose services in an isolated environment with startup, health, termination and data recovery checks. Detection reads configuration only and never runs build/up/pull or changes the host daemon.

Source: [Official reference](https://docs.docker.com/build/building/best-practices/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
