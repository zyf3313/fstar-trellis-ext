# Maven engineering baseline

**Trigger:** The target package declares or has parsed evidence for `maven`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Run selected modules through their actual reactor root with required dependencies. Review parent/BOM/plugin management and active profiles; stale locally installed siblings cannot substitute for reactor evidence.

- Preserve wrapper/Maven, compiler release and toolchain selection separately. Distinguish dependency versions from plugin/parent inheritance; unresolved properties require parent/settings review rather than guessed numbers.

- Validate the configured lifecycle with test/skip counts and artifact scope. The presence of pom.xml does not identify an installed Maven version or authorize downloads/build execution during detection.

Source: [Official reference](https://maven.apache.org/guides/mini/guide-multiple-modules.html). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
