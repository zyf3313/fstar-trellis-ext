# Prisma engineering baseline

**Trigger:** The target package declares or has parsed evidence for `prisma`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Identify installed Prisma major and its actual schema/contract, generated-client output and database connector. Keep generator/runtime versions aligned; regeneration and migrations are reviewed project actions.

- Pass the transaction owner through related writes and keep external calls/retry/idempotency outside inappropriate transaction lifetimes. Supported engines, isolation, timeout and nested transaction behavior vary by release.

- Test generated types, uniqueness/concurrency failures and migration drift with the selected engine. Never infer a database server release from the client or apply current Prisma APIs to an older project.

Source: [Official reference](https://www.prisma.io/docs/orm/fundamentals/transactions). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
