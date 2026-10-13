# Electron engineering baseline

**Trigger:** The target package declares or has parsed evidence for `electron`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Separate main, preload and renderer privileges. Enable context isolation and expose narrowly scoped preload capabilities; validate IPC message payloads and sender ownership before privileged work.

- Keep untrusted renderer content away from unrestricted Node APIs. Own windows, listeners and background processes through close/quit paths, and use the actual navigation/permission policy.

- Test bridge contracts, denied IPC/navigation and resource shutdown, then package for the target OS. Browser preview tests do not validate Electron privileges, signing or update behavior.

Source: [Official reference](https://www.electronjs.org/docs/latest/tutorial/context-isolation). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
