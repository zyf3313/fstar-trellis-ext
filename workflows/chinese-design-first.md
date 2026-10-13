# Personal Chinese Design-First Workflow

Read `.trellis/spec/guides/personal/index.md` for current-phase and target-area rules.
Use project-specific package/layer constraints before implementation. User-facing documents and reports are Chinese; AI instructions are concise English.

## Phase Index
```
Phase 1: Plan → discuss, explore, PRD, applicable UI/TDD, review and freeze
Phase 2: Execute → implement the confirmed design and verify affected scope
Phase 3: Finish → synchronize docs, capture specs, commit and wrap up
```

## Phase 1: Plan
New projects and large cross-module/system/architecture/migration/compatibility tasks use full planning. Small changes retain the lightweight path with an existing design basis.
#### 1.0 Create task `[required · once]`
Reuse current task consent/identity. Create a Trellis task after the applicable user consent; creation alone does not approve implementation.
#### 1.1 Requirement exploration `[required · repeatable]`
Use Trellis brainstorm and `personal-design`. Clarify scope, non-goals and observable acceptance. Inspect available evidence before questions. Complex work needs task prd.md/design.md/implement.md, referencing authoritative user docs.
#### 1.2 Research `[optional · repeatable]`
For new projects, large work or key choices use `personal-project-explore`. The tools/exploration/usage.md rule owns routing and adjustable budgets: explicit source/provider first, reuse capabilities/evidence, fill selected gaps on demand. Verify focused originals/source and save Chinese adoption/fit decisions linked to PRD/TDD/UI. Completion covers selected capabilities; `not_requested` sources do not block it, selected unavailable requirements remain pending/restricted. Report actual client loading separately.
#### 1.3 Configure context `[required · once]`
Select only applicable package/layer/stacks/capabilities. Inline execution skips subagent JSONL curation; dispatch platforms curate required manifests.
#### 1.4 Activate task `[required · once]`
Present Chinese PRD and TDD; UI projects first confirm global language/shell and affected interactions. Freeze covered versions and actual user confirmation. Start only after approval of the latest reviewed design. Carry that authorization through routine work.

UI planning uses the installed Impeccable skill with focused UI UX Pro Max lookups. Existing UI work preserves its baseline. Preview and review precede application implementation; a combined provider build flow cannot bypass the design gate. `personal-project-init` repairs missing UI providers, and the UI tools rule owns installation/probe boundaries.
#### 1.5 Completion criteria
Scope and observable acceptance clear; product decisions resolved; applicable PRD/TDD/UI and task artifacts complete; latest review/confirmation evidence present; task status in_progress.

[workflow-state:no_task]
Classify the request and reuse existing authorization. Use `personal-project-init` for project adoption/repair; discuss target stack for blank projects. New/large work enters Trellis planning.
[/workflow-state:no_task]
[workflow-state:planning]
Use Trellis brainstorm and `personal-design`; stay in planning until latest-design review. Explore reference choices, prepare Chinese PRD/TDD and applicable UI. Complex tasks also have design.md/implement.md.
[/workflow-state:planning]
[workflow-state:planning-inline]
Use Trellis brainstorm and `personal-design`; prepare complete planning artifacts and latest-design review. Inline skips JSONL curation. Do not implement before confirmed scope.
[/workflow-state:planning-inline]

## Phase 2: Execute
#### 2.1 Implement `[required · repeatable]`
The main session owns planning, dispatch, progress and acceptance. In Trellis dispatch mode, send approved implementation to `trellis-implement` with `Active task: <task path>`, curated implement.jsonl, exact file ownership and applicable checks. The execution agent loads task artifacts/specs and implements directly without recursively dispatching execution agents. Implement confirmed contracts/token/components/interactions using focused CodeGraph/QMD/RTK and conditional database rules. An explicitly selected inline mode instead uses trellis-before-dev in the main session.
#### 2.2 Quality check `[required · repeatable]`
In dispatch mode use a separate `trellis-check` agent with the active task, curated check.jsonl and final changed scope. Review and fix findings, then rerun affected gates. Inline mode uses the trellis-check skill in the main session. Keep full logs and real behavior/visual/platform evidence. The main agent evaluates the findings and final acceptance. Trace requirement → design/UI → protocol/code → acceptance. Do not treat build/import-file generation as user/platform acceptance.

For changed UI, use a scoped Impeccable detector pass alongside project quality and browser checks. Apply the project's inline/delegation policy and report actual coverage; a clean source scan does not prove rendered accessibility or usability.
#### 2.3 Rollback `[on demand]`
Material product/contract/UI changes update affected authority/artifacts/acceptance and return to scoped review. Internal changes retain prior approval. Database recovery respects engine/transaction outcome.

[workflow-state:in_progress]
The main session supervises: dispatch trellis-implement → separate trellis-check → assess final affected scope and design consistency → trellis-update-spec → commit → finish-work. Begin each dispatch prompt with Active task: <task path>; execution agents load their curated JSONL and current PRD/design/plan, preserve other work and do not recursively dispatch implement/check agents. Follow the actual project's dispatch policy; do not dispatch when the active runtime requires inline. Reconfirm only changed design scope.
[/workflow-state:in_progress]
[workflow-state:in_progress-inline]
Main agent reads artifacts/specs, implements and owns final checks. Read-only scouts may research under project rules. Preserve frozen design mappings; invalidate changed generated/evidence versions.
[/workflow-state:in_progress-inline]

## Phase 3: Finish
#### 3.2 Debug retrospective `[on demand]`
Record a reusable prevention contract when a meaningful failure revealed one.
#### 3.3 Spec update `[required · once]`
Use trellis-update-spec; place reusable learning in its owning category/project layer. Keep private business data outside shared templates.
#### 3.4 Commit `[required · once]`
Verify final affected scope and document consistency; commit only owned work under the user's repository instructions.
#### 3.5 Wrap-up reminder
Use trellis-finish-work. Report completed/failed/skipped and real acceptance separately. Archive only actually completed work; preserve outstanding external/runtime gates.
[workflow-state:completed]
Wrap up after verified completion; no artifact/test substitutes for unmet acceptance. Preserve release/install/rollback evidence and remaining user-owned actions.
[/workflow-state:completed]
