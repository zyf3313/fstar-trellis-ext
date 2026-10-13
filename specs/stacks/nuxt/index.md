# Nuxt engineering baseline

**Trigger:** The target package declares or has parsed evidence for `nuxt`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Confirm Nuxt major, directory conventions and rendering/deployment mode. Nuxt 2 and 3/4 have different server/build integrations; consult the selected version before changing APIs or folders.

- Separate public/private runtime configuration and server-only code. Keep user state scoped to the request and review async data keys, hydration and invalidation for cross-user leakage or stale results.

- Validate routing, error handling and server/client output through the configured Nitro/legacy target. Static output and a running server require different deployment checks.

Source: [Official reference](https://nuxt.com/docs/guide/concepts/server-engine/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
