# Optional document consistency

Use when a project already maintains product, technical or UI design artifacts, or
when the user requests them. Scope the artifacts to the work; a small edit does not
require a PRD, TDD, research report or UI design.

Identify each authoritative source and its version. Update affected requirements,
contracts, UI assets and acceptance references when behavior changes. Generated
projections should identify their source and preserve local edits. A change in an
implementation detail only needs the project's applicable evidence.

Record real user confirmation separately from synthetic fixtures or mechanical
hash/link checks. Keep unresolved platform, device and environment checks explicit.
For requested Chinese PRD/TDD generation, template source lookup and scoped design
confirmation, use [product and technical design](product-technical-design.md).
Reuse existing confirmation; materially changed design needs review of the affected
part. The optional templates and UI example do not impose a gate on every task.
