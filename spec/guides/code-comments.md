# Code comments

Use comments to preserve information that the code cannot state clearly by itself:
complex business rules, non-obvious decisions, constraints, side effects,
compatibility behavior and reasons a simpler-looking approach is unsafe.

Prefer clear names and small cohesive code over commentary. Do not translate each
line, restate a signature, narrate obvious control flow, or require a comment on
every function. Public API documentation follows the owning project's language,
framework and spec conventions; this guide does not replace them.

Place the comment next to the behavior it protects. State the reason or invariant,
and link a stable requirement, issue, protocol or migration only when that source
will remain useful. Avoid dates, authors and temporary history that version control
already owns.

When code changes, update or remove affected comments in the same change. A stale
comment is a defect. Review comments together with tests and contracts so they
describe current behavior, including compatibility and failure boundaries.
