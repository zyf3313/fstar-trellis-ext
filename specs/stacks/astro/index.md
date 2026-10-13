# Astro engineering baseline

**Trigger:** The target package declares or has parsed evidence for `astro`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Record static/server output, deployment adapter and framework integrations. Keep server-rendered content separate from interactive islands and hydrate only components that need browser behavior.

- Choose hydration timing from user interaction and payload cost. Validate content/data at build/request boundaries and avoid placing private values in client props or public environment variables.

- Test generated routes/assets, island interactions and target deployment behavior. Client-only and SSR islands have distinct loading/fallback paths; a successful static build does not certify server execution.

Source: [Official reference](https://docs.astro.build/en/guides/islands/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
