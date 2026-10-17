# Chinese product requirements and technical design

Use within native Trellis discussion/planning when the user requests a Chinese
产品需求说明 or 技术方案. For a new project, large iteration or substantial task, first let native
Trellis requirements and design converge, then ask once before implementation
whether the user wants the 产品需求说明, 技术方案, both or neither. Do not ask again when
the user already requested or declined them for this scope. Small fixes do not
trigger the question or full documents; reuse existing design and update only
affected sections. Produce Chinese artifacts
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

- [产品需求说明](../templates/prd.zh-CN.md)
- [技术方案](../templates/technical-design.zh-CN.md)
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
   project content. Prefer existing project locations. When none exist, use the
   optional requirement layout below; do not create empty files just to match it.
3. Write the 产品需求说明 for reading: background/scope, business flow, then modules.
   Within each module keep responsibilities, functions, business rules, fields,
   exceptions and acceptance together. Field tables cover source, required,
   length/range, format, default, editable conditions, validation and dictionary
   `typeCode` where applicable. The 产品需求说明 references the stable typeCode; it
   does not duplicate a second list of implementation values.
4. Write the 技术方案 in this order: understanding/scope, overall technical
   solution and panorama, entity/state/storage structure, module technical design,
   then applicable special designs, migration/release, tests, impacts/open
   decisions, configuration and appendices. Apply project-type profiles per
   module and trim inapplicable sections.
   Do not force Java, REST, relational tables, response wrappers or DDL onto other
   project types. Express actual page/component/platform contracts for UI,
   signatures/arguments/output/exit codes for CLI/SDK, schemas/checkpoints/replay
   for data/async work, and resource/configuration/lifecycle/rollback contracts for
   infrastructure. Data/state ownership remains explicit even without a database.
5. For **each function in the 技术方案**, specify the mechanism and why it fits, entry point,
   responsible components and dependencies, real inputs/outputs/state, validation,
   key processing steps, applicable authorization/concurrency/transaction bounds,
   failures and recovery, compatibility/consumer impact, and tests tied to acceptance
   IDs. Module and applicable special-design sections must cover every in-scope
   function; a system architecture
   picture or generic API outline alone is insufficient.

## Large-document generation and revisions

For long documents, establish the applicable outline and module/function coverage
first, then write bounded sections into the same authoritative file. Review each
section against its confirmed facts before continuing; do not rely on one oversized
response to preserve every template requirement. Reuse prior approval instead of
asking the user to approve each mechanical writing step. At the end, cross-check
module coverage, field/dictionary links, diagrams, contracts and open decisions.

When the user corrects a section, update it in place and check dependent sections,
related artifacts and the preview. Do not regenerate unrelated approved sections
or maintain separate “for review” and “for AI” copies. If work is interrupted,
record the last completed section and remaining gaps in the existing task record;
resume there without presenting an incomplete document as ready for acceptance.

## Requirement and asset locations

Use the project's existing convention first. If none exists, this optional default
keeps one requirement version together:

```text
docs/requirements/YYYY-MM-DD-slug/
  README.md
  product-requirements.md
  technical-design.md
  test-cases.md
  test-runs/<run-id>.md
docs/requirements/archive/YYYY-MM/YYYY-MM-DD-slug/
design/ui/
design/prototypes/
review/
```

The requirement `README.md` records identity, status, related native Trellis tasks,
authoritative files and UI/prototype asset versions. One requirement may link
several native tasks; each task links the requirement version and modules it owns
instead of copying the full product or technical document.

Native tasks follow native archive behavior. Archive the requirement separately
after its related delivery and acceptance are complete, then repair links. Long-lived
UI sources and runnable prototypes stay under `design/`; do not move them into the
requirement archive. The archived requirement records an immutable commit or asset
version. Drafts may temporarily name a working version, but must not present it as
an immutable baseline.

## Explain with diagrams and applicable UI

The 产品需求说明 needs a business panorama and a business diagram for each function. The 技术方案
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

In this document-design scenario, present the current requested 产品需求说明/技术方案 and
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

Configuration is authoritative in the 技术方案: list only actual maintained values
and their meaning. A configuration change must not silently override a confirmed
business decision in the 产品需求说明. Update both documents and re-review the affected
decision when behavior changes.

Before delivery, check Chinese readability, no example/placeholder masquerading as
fact, module/function coverage, appropriate diagrams and contracts, traceability,
open decisions, actual source/version/confirmation and cross-document consistency.
Separate document completeness, implementation, automated checks, real environment
checks and user acceptance; unperformed checks remain pending with their gaps.
