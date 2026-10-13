# Node.js engineering baseline

**Trigger:** The target package declares or has parsed evidence for `node`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Confirm package type, ESM/CommonJS boundaries, engine declarations and selected lockfile runner. Built-in API availability comes from the project Node runtime, not the tool installer runtime.

- Keep synchronous CPU/blocking work away from request IO; bound concurrency and backpressure. Own timers, listeners, sockets and child processes, including shutdown and abort cleanup.

- Handle rejected promises at their owner, preserve error exit codes and signal behavior, and test process termination/resource release. Never execute a discovered package script during detection.

Source: [Official reference](https://nodejs.org/api/process.html). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
