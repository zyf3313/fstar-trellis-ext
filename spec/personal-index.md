# Personal scenario index

Use this page only when the project has explicitly selected the personal library. The project's native Trellis workflow, existing spec index, task records and local instructions remain authoritative. Link this page once from the project index or the relevant task JSONL, then load only the guide and template required by the current scenario.

## Scenario routing

| Trigger | Read | Optional local template |
|---|---|---|
| Chinese PRD/TDD requested, a new project, or a substantial design task | [Product and technical design](guides/product-technical-design.md) | [PRD](templates/prd.zh-CN.md), [TDD](templates/technical-design.zh-CN.md), [type profiles](templates/technical-design-profiles.zh-CN.md) |
| New interface, interaction change, or UI review | [UI design](guides/ui-design.md) | [UI baseline](templates/ui-baseline.zh-CN.md), [feature interaction](templates/ui-feature.zh-CN.md) |
| Existing product, technical, UI, implementation or evidence changes | [Document consistency](guides/document-consistency.md) | [Change review](templates/review-change.zh-CN.md) |
| Definition, signature, call graph or impact question | [Code search](guides/code-search.md) | — |
| Cross-document discovery or past-decision lookup | [Knowledge search](guides/knowledge-search.md) | — |
| Current external fact, source verification or reference-project exploration | [Web research](guides/web-research.md) | [Exploration](templates/exploration.zh-CN.md) |
| Schema/data inspection or an authorized database change | [Database access](guides/database-access.md) | — |

Known small files and stable local facts should be read directly. A task may combine routes, but should not load every guide or template by default. No UI change means skip UI design; a small implementation fix should reuse existing design and update only affected records.

## Delivery and evidence preferences

Write user-facing explanations and authored deliverables in Chinese unless the user requests otherwise. Keep identifiers, protocol names, source quotations and tool commands exact. Read foundational design and the exact code before editing; preserve unrelated work and reuse authorization already granted for the same scope.

Treat tool choice, installation/discovery, client loading, task execution and successful acceptance as separate states. These guides choose routes such as CodeGraph, QMD, GitHub/gh, optional DBHub and Emil only when their scenarios apply. They do not install tools, download models, create indexes, connect accounts/databases or alter model settings. If a selected capability is unavailable, use the guide's fallback or report the gap.

Report implementation, automated checks, environment/device checks and real user acceptance separately. Reuse evidence only when code/content state, environment, command and scope are unchanged. Hashes, links, generated files and passing tests do not by themselves prove semantic consistency, platform compatibility or user confirmation. Keep skips and unresolved checks explicit.
