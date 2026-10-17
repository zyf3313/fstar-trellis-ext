# Document consistency

Use when a project already maintains product, technical or UI design artifacts, or when the user requests them. Scope the artifacts to the behavior that changed. A small internal edit does not require a new PRD, TDD, research report or UI design.

## Change matrix

| Change category | Inspect and update when affected | Confirmation and evidence |
|---|---|---|
| Product scope, goals, roles, rules or acceptance | PRD, related TDD/UI, task requirements and requirement-to-acceptance mapping | Review changed behavior only; keep unrelated approval |
| Technical contract, state model, data, migration or compatibility | TDD, actual protocol/schema/migration, consumers and tests; update PRD/UI only when user behavior changes | Record contract/version, compatibility, migration and recovery evidence |
| Global UI language, tokens, components, frame or navigation | UI baseline and authoritative design source, affected features, boards/previews/prototypes/exchange files and implementation components | Invalidate old visual/interaction evidence; regenerate and recheck affected outputs |
| Feature interaction, validation, feedback or failure recovery | Feature UI document, source/state mapping, related PRD/TDD, implementation, tests and preview | Confirm the changed path and reuse existing approval outside it |
| Internal implementation with no observable/contract change | Necessary implementation notes and engineering verification | Do not force product-document changes or new user approval |

Classify mixed changes in every applicable row. “No update” is a conclusion that should name the checked artifact and why it is unaffected, not an assumption based on file type.

## Executable propagation loop

1. Identify each authoritative source, current version, ownership and actual confirmation scope.
2. List affected requirements, functions, contracts, diagrams, UI states, generated/platform artifacts, implementation locations, tests and acceptance evidence.
3. Edit the authoritative source first. Preserve stable IDs or record explicit old→new mappings.
4. Update or regenerate only affected projections and implementations from that source. Never hand-edit the same generated fact in multiple places.
5. Check IDs, versions, links, diagrams/tables and actual semantics across source, outputs, code and tests.
6. Run the verification appropriate to the change and record command/environment/scope, failures and skips.
7. Record the resulting version, invalidated evidence, remaining gaps and real user confirmation for the changed scope.

When a change belongs to a versioned requirement, update its `README.md` links and
the native task's requirement/module reference. When a requirement is archived,
repair incoming links but leave long-lived `design/ui/` and `design/prototypes/`
assets in place. Their current version and the immutable version referenced by the
archived requirement must remain distinguishable.

For previews, update the authoritative document or asset first, then regenerate the
manifest projection. Do not edit generated Storybook content as a second source.
Adding or deleting one optional document must not force unrelated artifacts into
existence. Missing sources, stale hashes/versions and broken routes are failures;
a successful static build alone does not prove the underlying tool or interaction.

Use [the change review template](../templates/review-change.zh-CN.md) when a durable record helps; it may be incorporated into an existing design or native task record rather than creating another planning system. For requested Chinese PRD/TDD generation, use [product and technical design](product-technical-design.md). For design source and UI output rules, use [UI design](ui-design.md).

## Conflict and evidence rules

A platform edit must be read back into the authoritative source or have an explicit, verified synchronization path. When origin, ownership or local-edit status is unclear, compare before writing and preserve the local version; do not overwrite it with a generated or registry copy. Keep source and generated/platform versions explicit so future work knows which side is authoritative.

Reuse old evidence only when content/code state, environment, command and scope are unchanged. Any relevant change, merge, failure or skipped gate requires fresh evidence for that scope. A hash, valid link, generated file or passing automated test cannot replace semantic comparison, target-platform behavior or user confirmation. Record implementation, automated checks, environment/device checks and real acceptance separately.
