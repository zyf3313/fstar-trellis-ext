# Chinese product requirements and technical design

Use within native Trellis discussion/planning when the user requests a Chinese PRD
or TDD. For a new project, large iteration or substantial task, first let native
Trellis requirements and design converge, then ask once before implementation
whether the user wants the Chinese PRD, TDD, both or neither. Do not ask again when
the user already requested or declined them for this scope. Small fixes do not
trigger the question or full documents; reuse existing design and update only
affected sections. TDD means Technical Design Document. Produce Chinese artifacts
and follow the project's existing document locations and conventions. A request for
one document does not require both: cite existing requirements or technical context
for the other.

A task is substantial when it crosses business modules, systems or clients; changes
a core business flow, data model or public contract; needs migration, compatibility
or staged delivery; or needs non-engineering review and independent acceptance.
Local defects, copy/style changes and internal refactors without an observable
contract change remain small unless the user explicitly asks for the documents.

## Obtain the actual templates

The canonical templates are installed with this guide under `spec/templates/`:

- [PRD](../templates/prd.zh-CN.md)
- [TDD](../templates/technical-design.zh-CN.md)
- [Project-type profiles](../templates/technical-design-profiles.zh-CN.md)
- For UI work, [UI baseline](../templates/ui-baseline.zh-CN.md) and
  [feature interaction](../templates/ui-feature.zh-CN.md), as needed.

Read only the templates required by the requested artifact and project type. If a
template is missing from the imported `spec/templates/` directory, report the
missing registry content and do not claim template-based generation. Record the
project's personal-library fixed ref with the output so the template version is
traceable; no separate checkout, root-template lookup or tool installation is
required.

## Establish scope and write the documents

For complex or multi-module requirements, apply [module clarification](module-clarification.md)
inside native brainstorming before treating requirements as converged. Document
generation does not replace discussion; optional human documents are not required
to perform that clarification.

1. Reuse confirmed intent and design. Verify repository facts before asking about
   user intent, scope, compatibility or interaction choices. Record sources,
   exclusions, dependencies and blocking decisions in native planning. Resolve
   blockers for the current scope; keep unknowns explicit rather than invent facts.
2. Use the actual Chinese template, replacing examples and placeholders with real
   project content. Prefer existing document locations; otherwise examples are
   `docs/design/<slug>/prd.zh-CN.md` and `tdd.zh-CN.md`. These are examples, not a
   required directory scheme.
3. In the PRD, establish background, current work/problems, goals, roles and scope
   before the business panorama and end-to-end flow. Define business modules,
   responsibilities and handoffs; frontend/backend/database layers are not business
   modules. Expand each in-scope module into functions with entry/preconditions,
   normal flow, result, rules, permissions, exceptions/recovery and observable
   acceptance. Include applicable UI states, nonfunctional requirements, impacts,
   unresolved decisions and truthful review/version history. A developer checklist
   or one-line feature list does not substitute for business requirements.
4. Keep the TDD's twelve-chapter skeleton: understanding/scope, decomposition,
   entities/data, detailed function design, optional non-interface functions,
   optional scheduled work, historical data, tests/acceptance, impacts, open
   decisions, optional configuration, and references/review history. Apply the
   project-type profiles per module; preserve common requirements and mark
   inapplicable sections or trim optional sections and renumber consistently.
   Do not force Java, REST, relational tables, response wrappers or DDL onto other
   project types. Express actual page/component/platform contracts for UI,
   signatures/arguments/output/exit codes for CLI/SDK, schemas/checkpoints/replay
   for data/async work, and resource/configuration/lifecycle/rollback contracts for
   infrastructure. Data/state ownership remains explicit even without a database.
5. For **each TDD function**, specify the mechanism and why it fits, entry point,
   responsible components and dependencies, real inputs/outputs/state, validation,
   key processing steps, applicable authorization/concurrency/transaction bounds,
   failures and recovery, compatibility/consumer impact, and tests tied to acceptance
   IDs. Sections 4/5/6 must cover the decomposition's functions; a system architecture
   picture or generic API outline alone is insufficient.

## Explain with diagrams and applicable UI

The PRD needs a business panorama and a business diagram for each function. The TDD
needs a meaningful diagram per function or a reference to explicit nodes in a
shared diagram. Choose by question: Mermaid `flowchart` for steps/decisions/data
flow, `stateDiagram-v2` for lifecycle, `sequenceDiagram` for interactions, and
`erDiagram` for applicable entity relationships. Show relevant exceptions and
boundaries. Keep diagram IDs/nodes, prose, tables, contracts and requirement IDs
consistent. Mermaid in Markdown is the default; no extra drawing tool is required.

For redesign comparisons, follow the template's green solid added, red dashed
deleted, orange solid modified with old→new labels, and gray retained nodes;
solid edges mean new paths and dashed edges replaced old paths. Include text and
line styles as well as color. New projects show real new/external steps, not an
invented old workflow. Other diagram tools retain editable source and viewable
exports with IDs and reproduction instructions.

For UI work follow [UI design](ui-design.md): `emil-design-eng` is the single core,
and existing project baselines take precedence. Establish the design language,
framework/navigation, overall layout and key paths/states; confirm a new project's
language/layout and clarify feature interactions before implementing them. Reuse
already confirmed baselines. Map requirements/functions to pages, states and
design references. With no UI, explain applicability and skip this work.

## Review, task linkage and maintenance

In this document-design scenario, present the current requested PRD/TDD and
applicable UI scope to the user for confirmation before development. Reuse actual
confirmation already given for that scope/version; do not ask again. Record the
real confirmation reference, covered scope and version. Resolve current blockers
before freezing. A draft title, passing tests or hashes cannot stand in for review.
This does not impose a new document gate on unrelated non-UI work or small fixes.

Keep Chinese documents authoritative for human design. Native task `prd.md` remains
the task record: reference their paths, versions, scope, requirement/acceptance IDs
and necessary summary, and reference relevant sources in task JSONL. Avoid a second
full authoritative copy or repeatedly loading all templates and entire documents.
Maintain traceability from requirement → module → function → diagram/contract →
acceptance. Authors, reviewers, dates, status and approval must reflect actual facts;
unknowns belong in the open-decision table.

Apply [document consistency](document-consistency.md) when behavior/contracts or
design change: update affected authoritative prose, diagrams, UI, task references
and acceptance, invalidate affected old evidence, and review materially changed
parts before dependent development. Existing approval covers its recorded scope.
Pure implementation details use the project's applicable verification without
expanding approval scope. Update the source guide/templates at their owners for
reusable improvements, preserving the consuming project's fixed-ref provenance.

Before delivery, check Chinese readability, no example/placeholder masquerading as
fact, module/function coverage, appropriate diagrams and contracts, traceability,
open decisions, actual source/version/confirmation and cross-document consistency.
Separate document completeness, implementation, automated checks, real environment
checks and user acceptance; unperformed checks remain pending with their gaps.
