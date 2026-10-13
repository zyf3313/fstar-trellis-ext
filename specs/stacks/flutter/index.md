# Flutter engineering baseline

**Trigger:** The target package declares or has parsed evidence for `flutter`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Keep widgets declarative and put mutable business state under a chosen owner. Dispose controllers/subscriptions and avoid updating disposed widget state after awaited work.

- Model route/deep-link/back behavior and restoration explicitly. Platform plugins need platform permissions, native setup and error/retry paths; Dart SDK constraints do not establish Flutter SDK compatibility.

- Run configured unit/widget tests and platform builds; verify important navigation/input/accessibility flows on a device or emulator. Golden images and a host build cannot replace device integration checks.

Source: [Official reference](https://docs.flutter.dev/ui/navigation). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
