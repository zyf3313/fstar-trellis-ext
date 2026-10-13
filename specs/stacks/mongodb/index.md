# MongoDB engineering baseline

**Trigger:** The target package declares or has parsed evidence for `mongodb`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Choose embedded/reference structure from access patterns and enforce document validation, unique/index constraints and bounded query projections. Preserve identifier and schema-evolution semantics.

- Record server topology, read/write concerns and session ownership before relying on multi-document transactions. Driver version is not server version; retried writes/commands need deliberate idempotency and result reconciliation.

- Test index/query behavior and migration/recovery against the actual topology. DBHub is not selected for this profile; choose and verify a compatible MongoDB provider before claiming inspection/write capability.

Source: [Official reference](https://www.mongodb.com/docs/manual/data-modeling/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
