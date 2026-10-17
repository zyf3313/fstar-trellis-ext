# Personal scenario index

Use this page only when the project has explicitly selected the personal library. The project's native Trellis workflow, existing spec index, task records and local instructions remain authoritative. Link this page once from an existing entry actually read in the relevant phase, then load only the guide and template required by the current scenario. Task implementation/check JSONL can activate those phases only; clarification needs a discussion-time entry.

## Scenario routing

| Trigger | Read | Optional local template |
|---|---|---|
| Large/complex or multi-module requirements, or explicit clarification/gap discovery | [Module clarification](guides/module-clarification.md) | Existing native PRD/open decisions; no extra template |
| Chinese PRD/TDD requested, a new project, or a substantial design task | [Product and technical design](guides/product-technical-design.md) | [PRD](templates/prd.zh-CN.md), [TDD](templates/technical-design.zh-CN.md), [type profiles](templates/technical-design-profiles.zh-CN.md) |
| New interface, interaction change, or UI review | [UI design](guides/ui-design.md) | [UI baseline](templates/ui-baseline.zh-CN.md), [feature interaction](templates/ui-feature.zh-CN.md) |
| Existing product, technical, UI, implementation or evidence changes | [Document consistency](guides/document-consistency.md) | [Change review](templates/review-change.zh-CN.md) |
| Definition, signature, call graph or impact question | [Code search](guides/code-search.md) | — |
| Cross-document discovery or past-decision lookup | [Knowledge search](guides/knowledge-search.md) | — |
| Current external fact, source verification or reference-project exploration | [Web research](guides/web-research.md) | [Exploration](templates/exploration.zh-CN.md) |
| Schema/data inspection or an authorized database change | [Database access](guides/database-access.md) | — |
| Test scope/cases/review, automation, execution, defects, regression or acceptance requested | [Testing and acceptance](guides/testing-acceptance.md) | [Cases](templates/test-cases.zh-CN.md), [execution report](templates/test-execution.zh-CN.md) |

Known small files and stable local facts should be read directly. A task may combine routes, but should not load every guide or template by default. No UI change means skip UI design; a small implementation fix should reuse existing design and update only affected records.

Clarification runs during native brainstorming: whole scope, module details, then
cross-module review. Confirming module names never confirms their unstated rules.
For discovery-time activation, reference this index from the project's existing
entry read by brainstorming; implementation/check JSONL alone is too late.

## Delivery and evidence preferences

Write user-facing explanations and authored deliverables in Chinese unless the user requests otherwise. Keep identifiers, protocol names, source quotations and tool commands exact. Read foundational design and the exact code before editing; preserve unrelated work and reuse authorization already granted for the same scope.

Treat tool choice, installation/discovery, client loading, task execution and successful acceptance as separate states. These guides choose routes such as CodeGraph, QMD, GitHub/gh, optional DBHub and Emil only when their scenarios apply. If a selected capability is unavailable, use the guide's fallback or report the gap.

For the five tool-backed routes—code, knowledge, UI, Web and database—first inspect
the current CLI, MCP, Skill, connector and built-in capabilities. A semantic match in
the table loads only that guide; it does not load all tool guides. Evaluate real fit,
permissions and data boundaries rather than name-only presence. Reuse an adequate
local equivalent. Otherwise the matched guide names the screened default, official
source, proposed action and impact. Ask the user before installation or configuration;
after approval the AI performs the stated action and verifies discovery, current-client
loading and a minimal real task. A user-selected tool has priority. Refusal, unsupported
environments and failed setup use the matched guide's fallback without repeated prompts.

Native `trellis init --registry ... --template personal-core --append` only imports
this `spec/` tree. It never installs or configures tools. Login, API keys, model
downloads, database credentials/connections, write access and external publication
remain separate authorization boundaries even after a tool installation is approved.

Testing requests reuse project frameworks and local capabilities under the same
soft-install policy. Generating/reviewing cases requires no tool installation.
Requirements and implementation are compared, existing tests reused, and only the
requested testing activity is performed; no new role or workflow phase is introduced.

Report implementation, automated checks, environment/device checks and real user acceptance separately. Reuse evidence only when code/content state, environment, command and scope are unchanged. Hashes, links, generated files and passing tests do not by themselves prove semantic consistency, platform compatibility or user confirmation. Keep skips and unresolved checks explicit.
