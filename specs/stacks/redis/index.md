# Redis engineering baseline

**Trigger:** The target package declares or has parsed evidence for `redis`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Give keys a namespace, type, TTL and ownership policy; bound collection size and distinguish disposable cache from authoritative state. Confirm persistence/eviction settings before promising durability.

- Use the actual atomic command/transaction/script semantics and keep multi-key operations compatible with cluster hash slots where relevant. Handle expiry, cache stampedes and reconnect/retry without duplicate business effects.

- Test TTL/eviction, concurrency and failure recovery against the target server/topology. Driver releases are not server releases; DBHub is not selected and a compatible provider remains pending.

Source: [Official reference](https://redis.io/docs/latest/develop/data-types/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
