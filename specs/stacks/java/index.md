# Java conventions

**Trigger:** Project declares Java.

Discover JDK/build versions from actual compiler/toolchain and Maven/Gradle configuration. Follow existing package/module dependencies, public types, null/error conventions and test framework. Validate from the correct multi-module root and selected dependencies, avoiding stale installed sibling artifacts. Java annotation/framework semantics require framework-specific evidence; do not copy fstar package names, JDK pin, identity model or deployment layout. Source: https://docs.oracle.com/en/java/ and the project's declared build-tool documentation. Record detected version and any unsupported contract before implementation.
