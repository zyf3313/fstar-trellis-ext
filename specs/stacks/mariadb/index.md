# MariaDB engineering baseline

**Trigger:** The target package declares or has parsed evidence for `mariadb`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Record MariaDB server/connector versions separately and inspect SQL mode, storage engine, collation/timezone and transaction isolation. A MySQL-compatible driver or protocol does not prove identical SQL behavior.

- Bind values and validate identifiers through the actual connector. Verify constraints, lock/deadlock behavior and implicit commits for the real migration; review recovery for already committed DDL/data changes.

- Use isolated engine tests and readback for migrations/writes, including unknown outcomes. DBHub is a documented adapter candidate; MariaDB connection/permissions/transaction behavior still require separate validation.

Source: [Official reference](https://mariadb.com/docs/server/server-management/variables-and-modes/sql_mode). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
