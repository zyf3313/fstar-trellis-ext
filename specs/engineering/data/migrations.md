# Data and migrations

**Trigger:** Schema or historical-data change.

Treat schema/history changes as versioned migrations owned by the project. Record scope, compatibility, execution time, pre/post checks and restoration/compensation; use the existing migration entry point. Reflect real entities/relationships/DDL and history treatment in TDD chapters 3/7/8/9. No database means no fabricated DDL. Verify target engine syntax and nontransactional DDL limits. Preserve identifiers, invariants and resource scope; a SELECT result limit is not a mutation bound.
