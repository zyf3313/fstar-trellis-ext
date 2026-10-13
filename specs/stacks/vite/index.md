# Vite engineering baseline

**Trigger:** The target package declares or has parsed evidence for `vite`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Record Vite/plugin versions, project root, aliases and selected package-manager runner. Keep browser and Node configuration contexts separate; public env substitutions must not include secrets.

- Review dev proxy versus production API origin, base paths and build output. Transform/plugin ordering and asset handling follow the installed release and target framework integration.

- Test both development interaction and built output on its deployment path. A running dev server does not prove production routing, imported assets or server-side functionality.

Source: [Official reference](https://vite.dev/guide/env-and-mode). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
