# Private Git registry transport

## 1. Scope / Trigger

Load when consuming a private registry or changing Trellis version/authentication. This contract targets the installed Trellis 0.6.9 resolver. Repository identity and visibility belong to the consuming project; do not infer them from a sample.

## 2. Signatures

```sh
trellis init --registry 'git@github.com:OWNER/REPO#FULL_COMMIT' --template personal-core --append
trellis workflow --template chinese-design-first --marketplace 'git@github.com:OWNER/REPO#FULL_COMMIT' --create-new
git clone --no-checkout git@github.com:OWNER/REPO.git SOURCE_DIRECTORY
git -C SOURCE_DIRECTORY checkout --detach FULL_COMMIT
git -C SOURCE_DIRECTORY rev-parse HEAD
python3 SOURCE_DIRECTORY/scripts/personal.py install --project TARGET --stack-registry SOURCE_DIRECTORY/stack-sources.json
```

Replace placeholders with the selected repository, a verified pushed 40-character commit SHA and independent paths. For a new project, also pass its selected platform/developer/noninteractive init flags. Declare selected stacks for an empty project.

## 3. Contracts

Existing SSH identity must have repository read access. The SSH source forces Trellis's Git backend: clone, fetch the selected ref, then detached checkout. No new token/env field is required; never store credentials in source URLs, specs, generated configuration or evidence. No global Git/SSH credential mutation is part of consumption.

Trellis 0.6.9's GitHub HTTP index uses unauthenticated fetch. A `gh:` source plus `GIGET_AUTH` does not authenticate that index. Private raw HTTPS consumption by the personal helper is separate and unverified. Use the same pinned local Git checkout for companion resources and its local source manifest; verify HEAD before running it. Native spec/workflow downloads do not install helpers, skills, templates, tools or hooks.

`--append` fills missing specs; it is not an upgrade merge. `--create-new` always writes `.trellis/workflow.md.new` and preserves the current workflow and hash record, regardless of local edits. Without that flag, a pristine workflow may be installed directly; local edits need explicit handling. Helper `install` uses its Base/Local/Target comparison and revision rollback. These are distinct operations. Library `not_published` and pending license indicate no formal release; authorized private source synchronization does not grant public publication rights.

Native bundle indexes and helper-selected indexes can differ during first combined initialization. Observed protected paths are `.trellis/spec/guides/personal/index.md`, `engineering/index.md` and `tools/index.md` under that personal directory. Helper exit 2 preserves current indexes and emits `.new.<hash>` candidates through its actions. Compare candidate/source/current content, merge links for actual project stacks while retaining local constraints, rerun install and verify the project indexes. Do not report all initialization completed while candidates remain unresolved. Same-ref protection is tested; cross-ref/version upgrade remains separate.

## 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| SSH key recognized and repository readable | Fetch actual pinned commit; compare downloaded source hashes |
| `ssh -T git@github.com` gives GitHub's successful-authentication greeting / exit 1 | Authentication probe succeeds; GitHub provides no shell |
| Missing identity, denied repository, nonexistent ref or download failure | Record failure; do not substitute mutable main or report consumption passed |
| Clone HEAD differs from selected SHA | Stop helper execution |
| Locally edited spec/workflow/helper-managed file | Preserve local bytes; inspect explicit candidate/protection result |
| Fresh native bundle + different helper-selected indexes | Exit 2 with protected index candidates; explicit project merge/recheck required |
| Private raw HTTP unavailable | Use the verified local checkout; do not claim HTTP authentication passed |

## 5. Good/Base/Bad Cases

- Good: independently consume spec and workflow at a pushed SHA, install companion resources from that exact checkout, verify local-edit protection.
- Base: private source with pending license; validate authorized private use separately from a future public release.
- Bad: trust an authenticated `gh` login to make the resolver's unauthenticated HTTP index work, or treat `--append` as an upgrade merger.

## 6. Tests Required

Assert remote visibility/commit and allowed file scope; pinned native spec/workflow bytes; repeated consumption preserves edits; conflict candidate matches source; copied helper runs independently; update/rollback preserve post-install edits. Record command exits, durations, actual ref, accepted/rejected states, and skipped environment gates. Recheck resolver behavior on a version change. Do not report different-version upgrade or public consumption without executing them.

## 7. Wrong vs Correct

Wrong: put a token in `gh:OWNER/REPO#main`, overwrite existing project files, and infer full initialization from a spec download.

Correct: use existing Git authentication, pin a verified SHA, separate native downloads from companion initialization, preserve local changes and keep publication/semantic acceptance separate.
