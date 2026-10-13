# Hibernate ORM engineering baseline

**Trigger:** The target package declares or has parsed evidence for `hibernate`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Identify Hibernate/Jakarta or javax persistence versions and the actual session/entity-manager owner. Preserve entity identity, equality and association ownership/cascade rules.

- Keep lazy loading within deliberate persistence boundaries; distinguish flush from commit and review query counts, optimistic locking and bulk updates that bypass managed-state synchronization.

- Test mapping/DDL and transaction conflicts against the actual dialect. Automatic schema generation is not a production migration plan, and JPA presence alone does not identify Hibernate as provider.

Source: [Official reference](https://hibernate.org/orm/documentation/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
