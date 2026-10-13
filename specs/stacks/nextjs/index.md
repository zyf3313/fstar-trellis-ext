# Next.js engineering baseline

**Trigger:** The target package declares or has parsed evidence for `nextjs`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Identify the installed version and actual App Router or Pages Router layout before editing routes. Preserve that routing model and place server/client boundaries deliberately; do not migrate routers as incidental cleanup.

- Keep secrets and privileged data on the server. Validate route/action inputs, scope authentication per request, and verify caching/revalidation behavior against the selected release rather than generic defaults.

- Test navigation, initial server output, hydration, mutation errors and production build/start on the actual deployment adapter. Version-independent guidance does not guarantee release-specific React/Next APIs.

Source: [Official reference](https://nextjs.org/docs/app). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
