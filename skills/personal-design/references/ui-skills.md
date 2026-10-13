# UI skill selection

Read only for UI planning, prototyping or review. These providers are the conditional UI initialization profile, not Trellis built-ins. As of 2026-10-13 Impeccable 4.5.2 / engine 0.1.14 and UI UX Pro Max CLI 2.15.0 have real installation/search/detector evidence in isolated consumers and the current project. Current-client automatic skill selection and hooks remain separately reported; the representative preview does not establish quality for every project.

## Select for the current job

| Job | Candidate | How to constrain it |
|---|---|---|
| Plan a new screen, shell or interaction before implementation | [Impeccable shape](https://impeccable.style/docs/shape/) | Reuse the PRD and answered questions; record structure, states, navigation and open decisions, then stop before implementation. |
| Find an initial style, palette, typography or stack-specific design advice | [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Retrieve relevant suggestions; translate accepted choices into the authoritative UI baseline. Existing baselines are not regenerated per page. Pass the actual target stack. |
| Produce a visual sample with a lighter design prompt | [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | Alternative primary designer; the confirmed brief and incumbent design system take precedence over aesthetic defaults. |
| Review or refine an existing preview | [Impeccable](https://github.com/pbakaus/impeccable) critique / audit / polish | Review the named module, feature or state. Request findings before edits when only review is authorized. Preserve identity and behavior; fix demonstrated issues within scope. |

Use one primary designer per stage. Initialization installs missing compatible providers using `tools.py`; load additional search or review guidance only when it answers a concrete gap. If installation or runtime remains unavailable, continue independent drafting with project guidelines and report the missing capability. Do not claim a command ran because its documentation was read. Follow project inline/agent-ownership rules even if upstream requests delegation, and disclose the review deviation rather than silently claiming its full dual-agent workflow.

For installed current versions, Codex uses `$impeccable shape ...`; other harnesses commonly use `/impeccable shape ...`. Verify the installed version and invocation rather than relying on older forum shortcuts. Do not use a combined design-and-build command to bypass the user's design confirmation.

## Preserve ownership and delivery

Existing product/UI sources remain authoritative. Provider context files such as PRODUCT.md, DESIGN.md or design-system/*/MASTER.md are projections or linked entry points with source IDs/version. Follow a provider's required schema when its detector depends on it; a link alone does not prove parsing or design-system checks work. Rebuild projections after source changes and invalidate stale evidence. Keep user-facing briefs, reports and review notes in Chinese. Respect the project's agent-ownership policy.

Skills do not replace the local preview scaffold, exchange-file generator, PRD/TDD, user acceptance or real runtime checks. Do not infer native Figma/MasterGo import support from a UI skill. Keep manual file export and preview verification in the normal design delivery pipeline.

## Verify a selected provider

Record origin/ref, license, runtime dependencies, supported client and actual write targets. Inspect installers before running them, merge rather than replace existing configuration, and separate skill discovery, engine availability, hook activation and browser integration. The current Impeccable installer includes hooks and its launcher may download an engine; installation alone does not verify those capabilities. Use one representative feature to check Chinese output, baseline preservation, required states, keyboard/responsive behavior and source/artifact consistency before reporting support.

[Agentation](https://github.com/benjitaylor/agentation) is an optional visual-feedback tool mentioned in community workflows. Its documented component requires React 18+ and desktop browsers; do not assume direct Vue integration. Assess the adapter and license separately before adding it to a preview. Do not install every candidate or promise a fixed token-saving percentage.
