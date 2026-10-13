# Fastify engineering baseline

**Trigger:** The target package declares or has parsed evidence for `fastify`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Respect plugin encapsulation and registration order for decorators/routes/hooks. Keep schema validation and response serialization at the transport boundary; do not expose internal error or model fields.

- Own resources in plugin lifecycle and close them with the server. Keep async hooks and callback hooks consistent, and verify authentication/parser/error scope within encapsulated contexts.

- Test requests with the configured injection/server approach and validate shutdown. Match schema compiler/plugin versions to the installed Fastify major before using release-sensitive APIs.

Source: [Official reference](https://fastify.dev/docs/latest/Reference/Encapsulation/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
