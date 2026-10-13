# SQLAlchemy engineering baseline

**Trigger:** The target package declares or has parsed evidence for `sqlalchemy`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Keep a Session/AsyncSession owned by one unit of work, not a shared concurrent request/task. Align model mappings and engine/driver versions with the project migration owner.

- Define commit/rollback/close scope and distinguish flush from commit. Review lazy loading and object expiration across session boundaries; async paths must not trigger unintended synchronous IO.

- Test transaction failure cleanup, query count and concurrent constraint behavior with the real engine. Match query/mapping APIs to the installed SQLAlchemy release rather than importing 2.x examples into legacy code.

Source: [Official reference](https://docs.sqlalchemy.org/en/20/orm/session_basics.html). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
