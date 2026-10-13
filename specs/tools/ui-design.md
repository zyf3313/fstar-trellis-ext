# UI design skills

**Trigger:** A project has a user interface or explicitly declares UI design work.

Initialization installs or repairs Impeccable and UI UX Pro Max using `scripts/tools.py`. Detect the actual UI stack, installed skill files and compatible runtimes; a blank UI project can declare `--ui`. Backend-only projects do not install this profile. Use fixed source commits and CLI versions from `tools.lock.json`. Reuse compatible assets; preserve local edits/deletions and existing hooks, with update candidates and recovery before-images. Probe the installed Impeccable engine and a deterministic scan, and run a real UI UX Pro Max search. Report engine, skill, client discovery and hook activation separately. Installation never means automatic hooks are active.

| Scene | Use | Required boundary |
|---|---|---|
| New project with no design direction | UI UX Pro Max relevant style/color/type/product queries; Impeccable shape | Confirm global language, shell/navigation and key interactions before application implementation. Suggestions are evidence, not accepted decisions. |
| New feature in an established project | Impeccable shape; focused UI UX Pro Max lookup only for a gap | Reuse the baseline and answered product questions; design affected states and paths first. |
| Existing preview needs review | Impeccable critique and its deterministic detector | Inspect rendered UX before detector synthesis; cite actual findings and project-specific review constraints. |
| Confirmed refinement | Impeccable polish; relevant UX/stack search | Preserve identity, business scope and behavior; synchronize source, documents, artboards, preview and acceptance. |
| Delivery | Detector plus project type/build/behavior/visual checks | Actual behavior, responsive layout and user acceptance remain separate from scan success. |

Use one primary designer per stage. Respect project agent ownership and authorization even when a provider asks for another workflow. In inline projects perform the review directly and disclose that deviation from a provider's dual-agent review. Native provider commands can differ by client; Codex skill invocation uses `$impeccable` / `$ui-ux-pro-max`, while CLI `shape` is not an executable subcommand. Use the installed skill instructions for design and the engine CLI for context/detection.

Provider PRODUCT.md/DESIGN.md/MASTER.md files are controlled projections or entry points to authoritative PRD/UI sources, with source version and correct schemas. Do not create an independent competing specification. User-facing briefs/reviews are Chinese. Retrieve relevant search results instead of loading the whole catalogue; recommendations do not authorize new features, dependencies or a palette reset. Keep raw evidence local and do not promise a fixed token saving.

## Executable adapter contract

### Scope / Trigger
UI projects use this conditional profile; explicit `--tools` repairs only selected providers. Installed library copies all helper scripts, so consumption is independent of the source checkout.

### Signatures
```sh
python3 .trellis/personal/library/scripts/tools.py --project . --ui
python3 .trellis/personal/library/scripts/tools.py --project . --tools impeccable ui-ux-pro-max
python3 .trellis/personal/library/scripts/ui_tools.py --project . --tool ui-ux-pro-max "table handling" --domain ux --max-results 3 --json
python3 .trellis/personal/library/scripts/ui_tools.py --project . --tool impeccable detect --json src/modules/example/
```

### Contracts
`tools.lock.json` carries CLI package/version, fixed Git source ref and the separate Impeccable engine version. Skill assets land in `.agents/skills/<provider>`, ownership manifests/backups/candidates in `.trellis/personal/ui-tools/`, raw logs in `.trellis/personal/evidence/`, and the current result in `tool-report.json`. Source download uses the fixed commit over HTTPS and records its digest; the cache is checked against its recorded files on reuse. Npm installation disables lifecycle scripts for these providers and verifies package/engine identity. Registry integrity metadata is recorded, not presented as an independently reproduced supply-chain attestation.

Explicit Impeccable calls set `IMPECCABLE_SKILL_DIR` and project-local `IMPECCABLE_HOME`; the packaged sibling engine is used, avoiding an implicit global cache dependency. Automatic hooks are optional and not enabled by asset installation. `client_discovery` is files-ready until actual client invocation is observed, and `overall_complete` stays false for that outstanding gate. Runtime binaries and evidence should be ignored by source control; skills carry their upstream license.

### Validation & Error Matrix
| Condition | Result |
|---|---|
| Compatible provider and unchanged skill | Reuse; rerun the representative runtime probe |
| Local edits/deletions or conflicting provider files | Preserve all local content; full candidate tree, `conflicts`, exit 1 |
| Unsafe source/archive/manifest path or skill symlink | Refuse before target mutation |
| Interrupted swap | Restore the before-image unless the new manifest identifies a committed transaction |
| Network/download/runtime unavailable | Provider `failed` with raw log; other providers continue; exit 1 |
| Explicit detector findings | Preserve engine exit 2; raw output remains in the evidence log |
| Successful source scan | Scope-specific evidence only; no claim of browser or user acceptance |

### Good / Base / Bad Cases
Good: Vue project installs/reuses both providers, queries relevant UX advice, preserves its baseline and checks the actual preview. Base: backend-only project skips this profile. Bad: skill files exist but engine invocation fails; report failed runtime rather than installed-and-ready.

### Tests Required
Verify conditional profile selection, idempotence, local edits and extra files, obsolete owned-file removal, symlink/archive refusal, swap recovery and exit-code preservation. In a disposable project execute a real search and detector handshake/scan, then repeat initialization. Independently copied library assets must include this helper/spec/reference and run without the maintainer checkout.

### Wrong vs Correct
Wrong: call `impeccable --version` and claim all capabilities ready, or run a combined build flow before design review. Correct: verify the engine handshake and real scan separately, record client/hook gaps, and preserve the Trellis design gate.
