# SQLite conventions

**Trigger:** Project declares SQLite.

Confirm database-file ownership, actual SQLite version, foreign-key enforcement, concurrency/journal behavior and migration strategy. Verify read-only/file permissions and transaction behavior with the selected driver/MCP. File-path or locking failures are not equivalent to successful rollback. Source: https://www.sqlite.org/docs.html ; do not inherit network database connection settings.
