# PostgreSQL conventions

**Trigger:** Project declares PostgreSQL.

Verify server version, schema/search_path, roles, indexes/constraints and transaction isolation. Bind query values with the project's driver/tool syntax. Migration DDL/data transformations need actual engine checks and recovery evidence. DBHub cancellation/statement_timeout and single-call transaction support must be verified for the installed version. Source: https://www.postgresql.org/docs/ ; do not reuse MySQL DDL or assume cross-call MCP transactions.
