# Tauri engineering baseline

**Trigger:** The target package declares or has parsed evidence for `tauri`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Keep Rust commands and front-end payload types aligned and validate values/paths at the command boundary. Apply least privileges to the actual windows/resources that invoke native capabilities.

- Identify Tauri major before editing allowlist/capability/plugin configuration: v1 and v2 schemas differ. Own native tasks, events and window lifecycle; never infer native permission from front-end checks alone.

- Test denied/invalid commands and platform packaging with the selected Rust/front-end toolchains. A web build cannot certify native plugins, signing or installed capabilities.

Source: [Official reference](https://tauri.app/security/capabilities/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
