# C# engineering baseline

**Trigger:** The target package declares or has parsed evidence for `csharp`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Read LangVersion, Nullable and analyzer settings separately from target frameworks. Preserve nullable contracts and validate external values before constructing application types.

- Pass cancellation through asynchronous IO; await owned tasks and avoid async void except platform event handlers. Dispose resources through using/await using as supported by the selected language/runtime.

- Test exceptions, cancellation and disposal on each selected target. Do not infer a C# language release from a .NET target or introduce newer syntax from host compiler availability.

Source: [Official reference](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
