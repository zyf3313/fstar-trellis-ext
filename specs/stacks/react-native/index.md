# React Native engineering baseline

**Trigger:** The target package declares or has parsed evidence for `react-native`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Record React Native, JavaScript dependencies, native Gradle/CocoaPods and platform toolchains separately. Keep native modules and JS protocol/types aligned; do not upgrade platforms as part of spec installation.

- Own subscriptions and app-state/navigation effects, and treat permissions/deep links/offline failures as platform behavior. Avoid expensive work on interaction paths; verify native resource cleanup.

- Test iOS/Android targets actually used, including build variants, native linking and device interactions. Metro/dev rendering is not proof of a release package or both platforms.

Source: [Official reference](https://reactnative.dev/docs/react-native-gradle-plugin). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
