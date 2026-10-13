# ASP.NET Core engineering baseline

**Trigger:** The target package declares or has parsed evidence for `aspnet`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Preserve middleware order, routing/authorization and request-scoped services. Bind and validate configuration under its environment owner; secrets must not enter client responses or source-controlled settings.

- Carry request cancellation to IO and keep background services within explicit dependency scopes. Map endpoint validation/domain errors consistently rather than leaking exception details.

- Test the actual host and selected target frameworks, including authorization, configuration precedence and shutdown. Match proxy/server and framework APIs to the installed ASP.NET release.

Source: [Official reference](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
