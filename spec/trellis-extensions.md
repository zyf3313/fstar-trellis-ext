# Trellis extensions

Use this page only when the project has explicitly selected the personal library.
The project's native Trellis workflow, spec indexes, task records and local
instructions remain authoritative. Link this page once from an entry that the
client actually reads, then load only the guide and template required by the
current request. Importing the files does not activate them automatically.

## Scenario routing

| Trigger | Read | Optional local template |
|---|---|---|
| Large/complex or multi-module requirements, or explicit clarification/gap discovery | [Module clarification](guides/module-clarification.md) | Existing native PRD/open decisions; no extra template |
| Chinese 产品需求说明/技术方案 requested, a new project, or a substantial design task | [Product and technical design](guides/product-technical-design.md) | [产品需求说明](templates/prd.zh-CN.md), [技术方案](templates/technical-design.zh-CN.md), [type profiles](templates/technical-design-profiles.zh-CN.md) |
| New interface, interaction change, UI review, or long-lived design/prototype work | [UI design](guides/ui-design.md) | [UI baseline](templates/ui-baseline.zh-CN.md), [feature interaction](templates/ui-feature.zh-CN.md) |
| Existing product, technical, UI, implementation or evidence changes | [Document consistency](guides/document-consistency.md) | [Change review](templates/review-change.zh-CN.md) |
| Complex rules, non-obvious decisions, side effects or compatibility boundaries need explanation in code | [Code comments](guides/code-comments.md) | Project language conventions |
| Definition, signature, call graph or impact question | [Code search](guides/code-search.md) | — |
| Cross-document discovery or past-decision lookup | [Knowledge search](guides/knowledge-search.md) | — |
| Current external fact, source verification or reference-project exploration | [Web research](guides/web-research.md) | [Exploration](templates/exploration.zh-CN.md) |
| Schema/data inspection or an authorized database change | [Database access](guides/database-access.md) | — |
| Test scope/cases/review, automation, execution, defects, regression or acceptance requested | [Testing and acceptance](guides/testing-acceptance.md) | [Cases](templates/test-cases.zh-CN.md), [execution report](templates/test-execution.zh-CN.md) |

Known small files and stable local facts should be read directly. A task may
combine routes, but must not load every guide or template by default. No UI
change means skip UI design; a small implementation fix should reuse existing
design and update only affected records.

Clarification runs during native brainstorming: whole scope, module details,
then cross-module review. Confirming module names never confirms unstated rules.
Implementation/check JSONL can activate later phases only; clarification needs a
discussion-time entry.

## Delivery and evidence preferences

Write user-facing explanations and authored deliverables in Chinese unless the
user requests otherwise. Keep identifiers, protocol names, source quotations and
commands exact. Prefer existing project locations. When none exist, the optional
default requirement and long-lived asset layout is defined in
[product and technical design](guides/product-technical-design.md) and
[UI design](guides/ui-design.md).

Treat tool choice, installation/discovery, client loading, task execution and
acceptance as separate states. For code, knowledge, UI, Web and database routes,
first inspect current CLI, MCP, Skill, connector and built-in capabilities.
Reuse an adequate local equivalent. Otherwise the matched guide may recommend a
screened tool; ask before installation/configuration and verify a minimal real
task after approval. Login, API keys, model downloads, database credentials and
writes, and external publication remain separate authorization boundaries.

Native `trellis init --registry ... --template personal-core --append` imports
this `spec/` tree only. It does not install tools, merge same-name files, replace
native indexes, or activate this entry automatically.

Report implementation, automated checks, environment/device checks and real user
acceptance separately. Reuse evidence only when content/code state, environment,
command and scope are unchanged. Hashes, links, generated files and passing tests
do not prove semantic consistency, platform compatibility or user confirmation.
