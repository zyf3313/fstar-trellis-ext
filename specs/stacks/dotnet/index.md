# .NET engineering baseline

**Trigger:** The target package declares or has parsed evidence for `dotnet`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Record global.json SDK selection, target frameworks, runtime identifiers and deployment mode separately. Restore/build/test the actual solution or selected projects; do not replace project targets to suit helper tools.

- Keep scoped services within their scope; singleton owners must not capture disposable request services. Own host shutdown and cancellation for background services.

- Check multi-target package compatibility and publish assets on their intended OS/runtime. A local build does not validate trimming, native dependencies or deployment readiness.

Source: [Official reference](https://learn.microsoft.com/en-us/dotnet/core/project-sdk/overview). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
