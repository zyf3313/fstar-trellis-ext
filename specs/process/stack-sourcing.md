# Project guideline sourcing and review

## 1. Scope / Trigger

New project, first adoption or explicit repair/update. Read existing project constraints. Identify package manifests, locks and confirmed architecture; discuss target choices for blank projects. `list-stacks` and `STACKS.zh-CN.md` list identification metadata for UI/database routing, not coding-rule coverage.

## 2. Signatures

```sh
python3 .trellis/personal/personal.py query-stacks --project .
python3 .trellis/personal/personal.py install --project . --offline
python3 .trellis/personal/personal.py install --project . --stacks python sqlite --stack-versions python=3.12.0
python3 .trellis/personal/personal.py install --project . --stack-registry PATH/stack-sources.json
python3 .trellis/personal/personal.py install --project . --stack-registry 'gh:OWNER/REPO/path#FULL_COMMIT_SHA'
```

Remote registries require a full 40-character commit. This helper registry is distinct from native `index.json`. `query-stacks` reports facts and optionally acquires explicit source data; `install` owns asset/report writes and revision rollback.

## 3. Contracts

The library contains 24 core/process/engineering/tools rules and no stack coding rules. Default `profiles` are empty. Default query/install makes no stack-source download or generic draft. It reports `project-spec-review-required`, `project_spec_complete=false` and `adaptation_complete=false`. Base asset installation remains usable for blank, known and unknown stacks. Project specifications must be reviewed and distilled from existing constraints, actual source and confirmed architecture, with concrete paths/examples/checks; keep those specifications in the project. Recognition or successful installation does not complete that review.

Explicit `--stack-registry` opts into reviewed project/credible sources, ordered personal → official → opensource. Schema 1 profiles require stable `id`, `stack`, `kind`, `major_versions` or boolean `version_independent`, `license`, `coverage[]`, and one source `path|url` with SHA256. HTTPS resources require ref, no credentials/query/fragment; relative remote paths inherit the registry commit. Official/opensource reference profiles require their own registry-relative `adaptation`; remote adaptation also requires `adaptation_sha256`. Local adaptation optionally verifies that digest. No library adaptation files are supplied. Raw reference data remains cache; only the selected adaptation becomes a reviewable project candidate.

Resources are UTF-8, bounded to 2 MB. Requests use a child deadline (20 seconds/request; 60 seconds/resolution). Offline uses hash-verified cache only. Never execute acquired scripts or change application dependencies. Successful explicit acquisition writes `.trellis/spec/guides/personal/stacks/<stack>/project-<scope-hash>.md` and a selected source index; failures and missing sources generate reports without generic rules. Four base category indexes remain; the stack index exists only for explicit project sources.

Reports `.trellis/personal/spec-sources.json` and Chinese `spec-sources.zh-CN.md` preserve package/manifest/version evidence, source/ref/digest/license/coverage, attempts, retrieval state and project-review responsibility. Failed source repair preserves the previous external project rule and records `adoption_state=preserved_previous_rule`, active source and conflicts. A newly acquired competing candidate uses `.new.<hash>`; failure alone does not manufacture a replacement draft.

The install report lists `project_spec_review_stacks` for ordinary review responsibilities, `unmatched_stacks` for source/version failures, and `unrecognized_stacks` only for names absent from identification definitions. An empty stack-rule catalog is intentional and does not constitute a matching failure.

Detection definitions retain 53 stable entries, exact dependency/config markers, capabilities and database routes. Keep all raw/version facts, language mode/SDK/runtime distinctions and parser gaps. Drivers never establish server versions. No scripts, dependencies or containers execute during detection. UI loads interface/tool rules; SQL routes a compatible provider; Redis/MongoDB retain provider selection pending. Confirmed blank declarations persist across repeat runs; actual conflicting facts remain authoritative. Consumer dispatch/AGENTS choices stay protected.

Withdrawn old stack files in the copied library or personal stack namespace are removed only when their current bytes match the old install baseline. Edited, newly added and unowned files are preserved and reported as conflicts. Retired source identities/digests in `withdrawn-stack-sources.json` are removal receipts only, with no rules, source paths or fetch URLs. Explicit project sources remain protected. Every deletion has revision backup bytes and a null post-delete hash; rollback restores absent files and refuses to overwrite post-delete recreation or edits.

## 4. Validation & Error Matrix

| Condition | Result |
|---|---|
| Default empty/no matching profiles | Base assets usable; project-spec-review-required; no stack draft/download |
| Explicit compatible source | Digest/ref verified; scoped candidate; project review pending |
| Explicit incompatible/unknown version | version_mismatch/version_unconfirmed; no incompatible rule |
| Conflicting facts/declaration | incomplete; preserve real evidence |
| Offline/cache miss, hash/download/deadline error | incomplete acquisition; preserve prior external rule |
| Invalid schema/path/ref/credential URL | Reject before spec adoption |
| Retired managed unchanged file | Remove with revision backup |
| Retired edited/unowned file | Preserve, report conflict |
| File recreated after deletion | Rollback conflict; preserve current file |

Exit 0 means this asset/query step passed, including an honest review-required default. Exit 2 means acquisition or adoption conflicts; exit 1 means invalid configuration/operational error. None proves semantic adaptation, tool/client readiness or full initialization.

## 5. Good / Base / Bad Cases

- Good: identify a Vue/SQL project, retain UI/database routes and review real project code before drafting its own specs.
- Base: blank confirmed Python/SQLite installs common assets and records project-spec-review-required.
- Bad: turn recognition into generic stack rules or overwrite an edited retired rule during upgrade/rollback.

## 6. Tests Required

Identification/version/runner and UI/DB routes; defaults with no network/drafts; explicit hash/ref/cache/offline/version/error boundaries; copied helper independence; retired managed-file removal, edits/new-file protection, repeat execution, interruption recovery and rollback recreation protection. Execute actual old-release upgrade in an independent Target separately from unit fixtures.

## 7. Wrong vs Correct

Wrong: install generic reminders for every detected stack and report project specifications ready.

Correct: install common assets, identify facts, source only explicit reviewed candidates and distill concrete specifications inside the real project.
