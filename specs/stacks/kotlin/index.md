# Kotlin engineering baseline

**Trigger:** The target package declares or has parsed evidence for `kotlin`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Confirm compiler/plugin, JVM target and Java interop types independently. Keep nullable platform types at the boundary; expose explicit domain nullability instead of spreading assertions.

- Give coroutine work a lifecycle owner. Propagate cancellation; close resources when cancelled and avoid detached scopes for request work. Choose dispatchers for blocking IO from the actual execution model.

- Preserve data-class equality/value semantics and module visibility. Test cancellation, exception propagation and Java callers with the configured Gradle/Maven target.

Source: [Official reference](https://kotlinlang.org/docs/coding-conventions.html). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
