# React project adaptation

Applies to React 18/19 common component/state contracts. Read the acquired official reference and local components before using release-specific APIs.

- Preserve pure rendering, component identity and stable list keys. Keep state with its owner; derive values during render rather than duplicating synchronized state.
- Follow Hook ordering and lifecycle rules. Effects synchronize external systems; use event handlers for user actions. Clean up subscriptions, timers and pending async work.
- Follow this project's router, state library, forms, query client and design components. Do not introduce another framework or choose client/server rendering without project evidence.
- Model loading, empty, failure, permission and recovery states. Use accessible controls and verify actual form/focus behavior.
- Locate project lint/type/test/build scripts and affected component tests. Build success alone is not interaction acceptance.

Scope excludes release-specific server components, compiler and framework routing. Confirm each of these against the actual dependency version when applicable.
