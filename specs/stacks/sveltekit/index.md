# SvelteKit engineering baseline

**Trigger:** The target package declares or has parsed evidence for `sveltekit`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Use the actual route layout and selected adapter. Separate server-only load/actions from universal/client code and expose only deliberate serialized data to the browser.

- Authenticate and validate per request/action; keep cookies and request state scoped. Model form failure/redirect/error results and invalidate relevant loaded data after successful mutation.

- Test deep links, form submission/recovery and server/client navigation on the target adapter. Prerendering constraints and framework error APIs require exact-version review.

Source: [Official reference](https://svelte.dev/docs/kit/routing). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
