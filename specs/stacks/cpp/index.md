# C++ engineering baseline

**Trigger:** The target package declares or has parsed evidence for `cpp`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Record language standard, compiler, standard library and ABI per target. Prefer RAII owners and value semantics; distinguish owning smart pointers from non-owning views/references with bounded lifetimes.

- Keep exception/error policy consistent across modules and foreign-function boundaries. Review move/copy invariants, iterator invalidation and synchronization instead of relying on incidental object lifetime.

- Use target-scoped CMake include/link/compile requirements. Test failure paths, memory/thread checks and binary compatibility where exposed; a C++ standard setting does not prove compiler feature support.

Source: [Official reference](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
