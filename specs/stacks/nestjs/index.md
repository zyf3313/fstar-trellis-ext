# NestJS engineering baseline

**Trigger:** The target package declares or has parsed evidence for `nestjs`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Preserve module imports/exports and provider scope. Controllers map transport contracts to services; guards/pipes/interceptors handle their existing authentication/validation/error responsibilities.

- Use lifecycle owners for resource setup/teardown and background jobs. Choose request/transient/singleton providers deliberately; a shared provider must not retain request-specific authorization state.

- Test dependency resolution, transport error mapping and selected HTTP/messaging adapter behavior. Verify exact-version decorators/security/configuration APIs instead of copying a current documentation snippet.

Source: [Official reference](https://docs.nestjs.com/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
