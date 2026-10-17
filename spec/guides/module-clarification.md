# Module-by-module requirements clarification

Use inside native Trellis brainstorming when a request is large/complex, spans
business modules, or explicitly asks to clarify requirements or discover omissions.
Module names alone are not converged requirements. For a small, clear change,
clarify only consequential gaps in the affected behavior; do not expand it into
whole-project discovery.

This guide adds no role, command, hook, installation, workflow phase or mandatory
human-facing document. Native task artifacts remain authoritative for decisions.
Use Chinese for questions, summaries and user-facing examples unless requested
otherwise.

## Establish the whole scope

Read relevant existing requirements, decisions and implementation evidence first.
Reuse prior confirmation; do not ask users to repeat repository facts. Existing
code describes current behavior, not automatic approval of desired behavior.
Keep five distinctions explicit: observed fact (with source), approved decision
(with scope), suggestion, open question, and deliberately deferred work.

Summarize the business purpose, main flow, modules, handoffs and in/out scope.
Let the user correct that map. Order module discussions by business flow and
dependencies, allowing the user to reorder them. Outline confirmation authorizes
the next discussion, not all module rules or implementation.

## Deepen one module at a time

Start with what is already known and identify the highest-impact unresolved
decision. Use the following as an internal gap checklist, not a questionnaire:

| Dimension | Discover applicable gaps |
|---|---|
| Flow | Actor, entry, prerequisites, steps, output, completion and next actor |
| Rules | Allowed/forbidden actions, calculations, uniqueness, ordering and limits |
| Fields/data | Meaning, source, requiredness, length/range, default, editability, dictionary values/typeCode where applicable |
| Permissions | Who can view/operate which records; ownership and data scope |
| State | States, transitions, permitted actions, cancellation, retry and recovery |
| Exceptions | Invalid input, duplicates/concurrency, empty results, dependency failure, interruption and boundary behavior |
| Handoffs | Upstream/downstream inputs, ownership and consequences of change |
| Acceptance | Concrete normal and material exception examples with observable outcomes |

Propose reasonable options with tradeoffs, clearly labeled as suggestions. Ask
about the highest-value decision per turn; offer related fields as a compact
suggested table for batch review rather than asking about each field separately.
Do not invent limits, defaults, dictionary codes, error behavior or acceptance
criteria to fill gaps. A technical implementation choice that does not affect
business behavior belongs in native design, not another business question.

After an answer, update its decision and dependent rules. Use a concrete scenario
to check shared understanding where ambiguity remains. Recap the module's confirmed
behavior, material open questions and deferrals before moving on. If a later
module changes an earlier assumption, name the conflict and reopen only affected
decisions and handoffs.

## Record progress without another planning system

Update existing native `prd.md` requirements/open decisions and applicable design
references. A compact optional table is enough; do not create a separate tracking
file, a mandatory template, or a full duplicate of human-facing documents:

| 模块 | 已明确 | 待确认及影响 | 下一步 |
|---|---|---|---|
| 申请 | 创建流程、字段约束 | 提交后能否修改，影响审批版本 | 讨论修改限制 |
| 审批 | 模块范围 | 驳回、撤回和重复审批规则 | 在申请规则确认后细化 |

These rows are illustrative, not project facts. Link evidence and real confirmation
in the existing record. Optional [product/technical documents](product-technical-design.md)
follow their own scenario rules and are never prerequisites for clarification.

## Cross-module review and convergence

Walk through the end-to-end normal path and material exceptions across modules.
Check shared fields/dictionaries, state transitions, authorization, handoffs and
observable acceptance for contradictions or missing behavior. Apply
[document consistency](document-consistency.md) only to affected maintained sources
and projections; [testing](testing-acceptance.md) may consume confirmed examples
when that activity is requested.

Claim convergence only for a named scope whose key rules, field constraints,
states, consequential exceptions, handoffs and acceptance outcomes are explicit.
Resolve blockers for that scope; record justified non-applicability and deliberate
deferrals. Question count, document size, a module list or user silence is not
evidence of completeness.

A short reply such as "可以" confirms only the clearly presented decision/scope it
answers. It cannot approve unspoken suggestions, unresolved questions or modules
not yet discussed. Ask a focused clarification only when the reply's referent is
ambiguous and consequential; do not repeatedly reconfirm a clear approval.

If the user wants development early, explain the resolved slice, remaining gaps
and dependency risks. Proceed only with the user's explicit bounded scope and
native phase/approval rules; preserve unresolved remainder and do not announce
whole-requirement completion. Module readiness alone never advances native phases.
