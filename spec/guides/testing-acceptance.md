# Testing and acceptance

Use when the user asks to analyze testing scope, generate/review cases, write
automated tests, execute tests, record defects, regress fixes or summarize acceptance.
Load only the requested activity and relevant project testing specs. This extends
the native Trellis workflow; it adds no role selection, mandatory phase, default
installation or document requirement to unrelated tasks. A case-generation request
does not authorize execution or business-code changes. Existing project quality gates
still apply.

## Inputs and bounded discovery

1. Reuse the stated object, goal, scope, test purpose and existing authorization.
   Ask only for missing decisions that affect the requested work.
2. For completed development, identify the intended change baseline and target
   revision, including relevant uncommitted changes. Read approved requirements,
   acceptance criteria, changed code, affected contracts and existing tests together.
   If no reliable diff baseline exists, name the inspected scope and limitation.
3. Start with the diff and existing tests; follow relevant callers, state transitions,
   validation, persistence and external effects. Use [code search](code-search.md)
   for structural questions. Do not scan the entire repository by default.
4. Requirements define expected behavior; implementation reveals branches, omissions
   and regression impact. Record both sources separately. Approved behavior missing
   from code must still have a case. Never derive the correctness oracle solely from
   the implementation under test.
5. For pre-development requests, generate a requirement-based draft and mark code
   comparison unavailable; supplement it after implementation. Unavailable code,
   documents or environment are explicit gaps, not reasons to invent evidence.

If approved requirements say 64 characters and code allows only 32, keep the
64-character expectation and flag the discrepancy. If code imposes an undocumented
daily cap, record observed behavior and an open decision, not a new acceptance rule.
Conflicting approved sources require clarification for affected cases; independent
cases can continue. Unknown policy, text, owner or threshold stays "待确认"; an
inapplicable field is "不适用" with a reason.

## Case generation and review

Use the user's existing template first. Otherwise read the
[case template](../templates/test-cases.zh-CN.md). Keep required semantics in its
fields or a compact linked detail; do not silently add many columns or drop
expected results to satisfy a format. Case generation and review need no installed
tool. Produce Chinese deliverables unless requested otherwise.

- Assign stable IDs; preserve existing IDs and reference reusable tests rather than
  generating duplicates. Record template/library ref and source versions.
- Cover applicable normal paths, boundaries, invalid inputs, authorization, state
  transitions, repeated/concurrent requests, failure recovery, data consistency and
  affected old behavior. Explain important exclusions; do not mechanically enumerate
  every dimension for every function.
- Include reproducible preconditions, concrete inputs and observable expected
  results linked to numbered steps/checkpoints. Simple data belongs in the step;
  complex data uses a versioned dataset reference. "Works correctly" is not an assertion.
- Separate test purpose (functional/performance/security) from execution level
  (unit/integration/API/E2E/manual). One case can map to several assertions or levels.
- Prioritize by impact and likelihood: high for core flow, data loss or unauthorized
  access; medium for meaningful recoverable errors; low for low-impact assistance.
  Use project priority rules first and state a short rationale.
- Add performance workload/concurrency/duration/metric and security surface/risk
  fields only for those purposes. Thresholds require an approved source. A baseline
  measurement without an agreed target is not a performance acceptance pass.
- Review requirement-to-case coverage, missing implemented branches, contradictions,
  duplicate intent, feasible setup and actionable assertions. Each in-scope
  requirement has cases or an explicit gap. Counts and AI coverage scores do not
  establish completeness. Critical unknowns block only the affected cases.

## Shared source and delivery self-check

Humans and AI use one authoritative Chinese case source. Generation alone defaults
to one case document; review updates that document and reports findings without a
mandatory separate review file. Split large documents by business module, never by
human/AI audience. Keep stable IDs across splits. Automation belongs in the project's
native test directories and references those IDs; it is executable verification,
not another editable case specification.

Default presentation is a concise table with details for complex cases. Optional
Storybook, detail views and coverage mind maps derive from the same source and IDs.
Do not maintain separate AI cases or preview-only facts, or install a portal just
to generate cases. Each execution adds a separate run report and needed evidence;
case definitions do not store a permanent "passed" status.

Before delivering or translating cases into automation, check:

- Label each numerical expectation's unit: business quantity, record count and
  event count differ. Recalculate expected values from the stated initial data;
  distinguish final totals from increments and isolate fixtures.
- Trace applicable state transitions and data conservation (for example, available
  and reserved inventory). Specify rollback and retry effects: failed operations
  leave no unintended partial changes; idempotent repeats add no duplicate effects,
  only where the approved contract requires this.
- Separate approved acceptance assertions from implementation observations. Do not
  promote unconfirmed payload fields, internal IDs or exact error text into business
  requirements. Mark missing premises "待确认" and name affected assertions.
- Recheck setup feasibility, scope coverage and duplicate intent against existing
  cases/tests. Fix ambiguous expectations before claiming cases are automation-ready.

For example, if an approved contract says one successful request creates one
reservation and one event, "quantity=2 means 2 records and 2 events" is wrong.
Write "reserve 2 items; add 1 reservation and 1 event; available stock decreases
by 2" with the initial stock and contract source. Do not assert an unconfirmed
event payload schema.

## Automation and tool selection

First inspect project test scripts/frameworks and locally available Skills, CLI,
MCP and browser capabilities; reuse adequate equivalents and the user's selected
tool. Pick the lowest level that verifies the behavior:

| Assertion | Usual level | Evidence limit |
|---|---|---|
| Pure validation, mapping or decision | Unit | Does not prove transport, database or UI behavior |
| Persistence, transaction, adapters, retry/idempotency | Integration | Record real versus substituted dependencies |
| Authentication, validation and public response contract | API | Does not prove user interaction |
| Critical user journey, rendered state and accessibility interaction | E2E/browser | Keep targeted; avoid duplicating every unit boundary |
| Device, subjective review or unavailable automation | Manual | Name executor/status; do not fabricate completion |

Map case IDs to existing/new tests and actual assertions. Mocks must not replace
the behavior being verified. Test missing behavior using requirement expectations;
do not weaken assertions, skip failures or rewrite business rules merely to go green.
Keep test-data isolation and cleanup explicit.

No third-party testing Skill is a default dependency. Requirement-only generation
instructions can be a reference; they do not replace code/diff and existing-test
analysis. Full test platforms are optional when the project already uses them.
If an execution capability is missing, present a bounded recommendation with
official source, reviewed version, proposed scope, downloads/service/data impact
and alternatives. Install/configure only after user consent, then verify discovery,
current-client loading and a minimal real operation separately. Refusal uses an
explicit manual/not-executed fallback; do not repeat prompts. Do not upload private
requirements, code or company Skills to an external evaluator without authorization.

## Execution, defects and regression

When execution is requested, establish target environment/revision, data scope,
commands and timeout. Preparation must fit existing authorization; destructive data,
load tests and external-system changes need their actual scope authorized, not just
permission to generate cases. Follow [database access](database-access.md) if applicable.

Use the [execution report](../templates/test-execution.zh-CN.md) or the project's
equivalent. Each run has a unique ID and references the exact case version/hash,
target code/content identity and environment; keep its report outside case definitions.
Record exact command/tool, environment, code/content identity, time,
executed/pass/fail/blocked/not-executed counts and evidence. Zero discovered tests,
generation success, mocks or a script exit alone do not prove end-to-end acceptance.
Redact secrets and keep evidence local unless sharing was authorized.

For each failure, distinguish product defect, test-script defect, environment/data
problem and unclear requirement. Record minimal reproduction, expected versus
actual result, affected case, evidence and impact. Repair only the authorized scope;
case generation or test execution does not silently authorize product changes.
Do not create a separate defect system unless requested.

Regression runs must verify the original failure plus affected dependencies/old
behavior. Create a new run report and link the prior failure, new revision and result.
Finalized run records and evidence are immutable; append a traceable correction
if needed, never overwrite an earlier failure or relabel old evidence as a new run.
Apply [document consistency](document-consistency.md): change expectations only when
their source is legitimately revised; update related cases, automation and generated
views, and invalidate stale evidence. Case definition version and run version differ.

Report generated cases, reviewed cases, automated scripts, actual execution,
environment/device gaps and user acceptance separately. Passing selected tests
supports only that tested scope; provide remaining risks and an acceptance
recommendation, never invent a user's approval.

## Reference candidates

These are optional references, not installed, empirically ranked or required tools:

- [myclaude test-cases](https://github.com/stellarlinkco/myclaude/tree/master/skills/test-cases):
  evaluate its case-design instructions against current project needs before reuse.
- [flow_test_engine](https://github.com/linlee996/flow_test_engine):
  reference candidate for clarification and case-generation organization.
- [WHartTest](https://github.com/MGdaasLab/WHartTest):
  reference candidate for case execution and evidence management.

An upstream source review, an isolated Skill output trial and a real platform run
are distinct evidence levels. Prefer no additional dependency until a representative
trial shows a benefit over the project's current capability.
