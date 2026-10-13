# Svelte engineering baseline

**Trigger:** The target package declares or has parsed evidence for `svelte`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Confirm Svelte compiler major and whether each component uses legacy reactivity or runes. Follow its existing mode; copying reactive syntax across modes can change ownership and update timing.

- Keep stores/component state under one owner and return cleanup for subscriptions, timers and DOM effects. Use stable keyed identity for stateful lists and avoid sharing request-specific state during SSR.

- Run the configured compile/type checks and test emitted events, reactive updates and unmount cleanup. Hydration and browser behavior still need runtime checks.

Source: [Official reference](https://svelte.dev/docs/svelte/overview). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
