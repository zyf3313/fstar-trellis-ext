# SwiftUI engineering baseline

**Trigger:** The target package declares or has parsed evidence for `swiftui`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Give observable state a stable owner and preserve view identity so updates do not recreate resources unintentionally. Select property wrappers/observation APIs for the actual OS/compiler availability.

- Keep UI mutations on the appropriate actor and cancel lifecycle-bound tasks. Treat navigation, sheets and asynchronous loading as explicit state transitions with recovery and restoration.

- Test state updates, task cancellation, accessibility and layout on supported OS/device sizes. Importing SwiftUI proves source usage, not the Swift compiler version or SDK feature compatibility.

Source: [Official reference](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
