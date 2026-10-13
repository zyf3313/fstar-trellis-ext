# Dart engineering baseline

**Trigger:** The target package declares or has parsed evidence for `dart`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Keep sound null-safety and public types explicit at IO/JSON boundaries. Respect package language constraints and analyzer options instead of raising the Dart SDK to satisfy example code.

- Handle Future failures and cancel owned stream subscriptions; close controllers/resources with their lifecycle. Isolates exchange supported messages and do not share mutable application objects.

- Run the actual analyzer/test targets and test error/cancellation paths. pubspec environment.sdk describes Dart; Flutter constraints and platform SDKs need separate evidence.

Source: [Official reference](https://dart.dev/effective-dart). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
