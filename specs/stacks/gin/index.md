# Gin engineering baseline

**Trigger:** The target package declares or has parsed evidence for `gin`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Keep route groups/middleware and request binding/validation under clear owners. Configure trusted proxies from the real topology and map domain errors to deliberate responses.

- Do not retain or concurrently reuse a request context after its handler lifecycle; pass copied/explicit data to owned goroutines. Propagate cancellation to downstream calls and bound server timeouts.

- Test handlers/middleware and actual HTTP-server shutdown. Confirm Gin/Go versions and selected server features independently; framework dependency versions do not determine the Go toolchain.

Source: [Official reference](https://gin-gonic.com/en/docs/server-config/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
