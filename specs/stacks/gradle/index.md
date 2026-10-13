# Gradle engineering baseline

**Trigger:** The target package declares or has parsed evidence for `gradle`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Use the selected wrapper and actual settings/project/task graph. Keep dependency constraints, plugins, version catalogs and convention plugins under their existing owners.

- Separate Gradle runtime JVM, application toolchains and Kotlin plugin/compiler. build.gradle.kts is a build DSL and does not prove the application is Kotlin; alias/dynamic configuration needs source review.

- Validate affected project tasks and configured tests, accounting for cache/up-to-date/skip results. Wrapper URL is configuration evidence, not permission to download or execute it during initialization.

Source: [Official reference](https://docs.gradle.org/current/userguide/multi_project_builds.html). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
