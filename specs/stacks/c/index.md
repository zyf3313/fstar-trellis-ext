# C engineering baseline

**Trigger:** The target package declares or has parsed evidence for `c`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Record C language standard, compiler/toolchain and target ABI separately. Headers expose stable ownership, length and error contracts; language-standard numbers are not compiler versions.

- Carry buffer lengths with pointers, check allocation/IO/size arithmetic, and give each allocation/file handle one release owner on every failure path. Avoid undefined behavior in aliasing, lifetimes and signed overflow.

- Build the actual CMake/other targets with project warning settings and applicable sanitizers. Test boundary sizes and resource failure cases on the intended architecture; the C11 committee draft is a reference, not a claim of full standard coverage.

Source: [Official reference](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
