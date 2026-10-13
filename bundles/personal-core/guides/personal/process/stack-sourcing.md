# Stack guideline acquisition and adaptation

## 1. Scope / Trigger

New project, first adoption or explicit repair/update. Browse all library coverage with `personal.py list-stacks` or the library-root Chinese `STACKS.zh-CN.md` overview; acquisition fixtures are not the coverage inventory. Read project rules first. Use actual package manifests/locks for existing code; discuss and declare targets for blank projects. Load only relevant package/stack sources.

## 2. Signatures

```sh
python3 .trellis/personal/personal.py query-stacks --project .
python3 .trellis/personal/personal.py install --project . --offline
python3 .trellis/personal/personal.py install --project . --stacks python sqlite --stack-versions python=3.12.0
python3 .trellis/personal/personal.py install --project . --stack-registry 'gh:OWNER/REPO/personal#FULL_COMMIT_SHA'
```

Local `stack-sources.json` is also accepted. Remote registries require a full 40-character commit; resolve an intended tag first. This helper registry is distinct from Trellis native `index.json`. `query-stacks` returns a plan and acquires/cache-checks data; `install` owns spec/report writes and rollback.

## 3. Contracts

- Project constraints remain authoritative. Candidate order: explicit personal profiles → compatible bundled personal baselines → official profiles → verified open-source profiles.
- A selected external personal profile supplies that scope's stack rule; do not simultaneously load a bundled rule as a competing authority. A different package may still need its independently selected bundled baseline.
- Registry: `schema_version: 1`; `profiles[]` have stable `id`, `stack`, `kind` (`personal|official|opensource`), `major_versions` or `version_independent`, `license`, `coverage[]`, and `source` with one `path|url` plus `sha256`. URL resources need `ref`; relative remote paths inherit the registry commit. Official/open-source references need a maintained library `adaptation` path.
- UTF-8 resources are limited to 2 MB each. HTTPS has no credentials/query/fragment. A child deadline bounds DNS/response time: 20 seconds per request, 60-second resolution network budget. Never execute downloaded examples/scripts.
- Hash-verified cache: `.trellis/personal/cache/specs/`. Reference data is private cache, not a complete executable project guideline. Offline misses stay pending.
- Scoped draft: `.trellis/spec/guides/personal/stacks/<stack>/project-<scope-hash>.md`. Base rules and five selected-category short indexes use the existing installer journal.
- Results: `.trellis/personal/spec-sources.json` and Chinese `spec-sources.zh-CN.md` record package/manifest/version evidence, profile/source/ref/digest/license/coverage, retrieval state, target paths, attempts and focused research queries. Provenance records are project assets; runtime cache stays ignored.
- On guarded repair, a row records `adoption_state: preserved_previous_rule`, `active_profile_id`, `active_source` and `candidate`; install returns `spec_adoption_conflicts`. The active source remains the previously adopted source across repeated failed repairs; candidate acquisition is not adoption.
- Reviewed detection: `stack-definitions.json` schema 1 has `groups[]` and `stacks[]` with stable `id`, group/name, Chinese coverage/detection summaries, capability/provider metadata and `markers[]` (`kind`, exact `names` or reviewed `prefixes`, boolean `version`). Parsers emit structured dependency/config facts; only matching facts select stacks. Add definitions and real rules/catalog or official profiles, then build/validate; this is separate from native `index.json`.
- New COMMON profiles are version-independent engineering mechanisms, not release API guarantees. Missing/unparseable versions remain `version_state` diagnostics and pending release/source review even when COMMON acquisition succeeds. Vue 2/Boot 2 have separate rule IDs/targets under the same stack ID; major-3+ profiles remain excluded.
- Bounded manifests include npm, Python, Maven/Gradle, Go/Cargo, Composer, csproj/global.json, pubspec, Swift Package/Xcode/SwiftUI imports, CMake, WeChat and Docker. Skip linked/ignored/generated preview paths. Kotlin DSL is not an application language. Java legacy aliases normalize with raw evidence. Keep language standard/mode, build SDK/tool version and runtime version separate. Driver versions never become server versions; exact official container image tags only establish configured targets.
- Runner commands reflect packageManager/nearest matching lockfile plus configured scripts; npm without evidence is only an example. Unsupported locks/YAML, TOML without a full parser, dynamic Gradle aliases/inheritance and unknown CMake languages require explicit declaration/source review; do not execute configuration to resolve them.
- Without packageManager, choose the nearest lock directory; conflicting runners at the same depth remain pending. Gradle coordinates count only in recognized static dependency calls, never arbitrary strings or comments; custom configurations/map notation stay diagnostic gaps.
- Preserve all version facts within and across manifests in a package. Compatible resolved/runtime pins may narrow ranges, while incompatible facts remain `version_conflict`. SemVer caret constraints with major zero and tilde constraints retain their actual upper bounds during explicit confirmation.
- Detection metadata routes UI capabilities and SQL providers. Redis/MongoDB stay database projects with provider selection pending; they do not auto-select DBHub. Do not silently rewrite consumer dispatch_mode or existing AGENTS policy.
- npm resolved lock evidence takes precedence over a declared range. Exact versions cannot be replaced by a contradictory declaration. Compatible explicit Python targets may narrow unbounded constraints. Driver versions never become database server versions.
- Confirmed blank-project stack/capability/version declarations persist on repeated runs. Explicit `--stacks` / `--capabilities` replaces its declaration list; passing an empty list clears that list, while actual detected packages still apply. A source/profile update does not silently change project selection.
- Discovered commands are configuration evidence, not executed checks. Common guidance does not prove runtime/release-specific API compatibility. Actual module/type/error/test adaptation remains AI work after source acquisition.

## 4. Validation & Error Matrix

| Condition | Result |
|---|---|
| Compatible personal source | Verify digest, generate scoped draft and preserve provenance. |
| Personal miss/mismatch | Try compatible official/open-source profiles; retain attempts. |
| Unknown stack | `missing_source`, draft gap and focused query; use available Web/MCP to read primary sources and register a reviewed profile. |
| Unknown/unbounded version | `version_unconfirmed`; do not claim release compatibility. |
| Incompatible major | `version_mismatch`; exclude incompatible bundled baseline. |
| Declaration conflicts with facts | `declaration_conflict`; preserve actual version. |
| Offline/cache miss, download/hash failure, exhausted budget | `acquisition_failed` or registry gap; no success claim or blind retry. |
| Invalid schema/path/ref or credential-bearing URL | Reject configuration before spec adoption. |
| Edited project rule/report | Preserve it, write `.new.<hash>` and retain owned rollback. |
| Previously acquired source fails during repair, or preferred source fails and falls back to a weaker guide | Preserve the previous project rule, create a pending candidate and report adoption conflicts; do not silently downgrade. |

CLI `0` means selected acquisition/assets passed, not semantic adaptation or tool/client readiness. `2` means incomplete/conflicting acquisition or asset conflicts, with usable independent assets retained. `1` means invalid configuration/operational error. Empty undeclared projects return `stack_undetermined` / `2`.

## 5. Good / Base / Bad Cases

- Good: React 19 and Go 1.x have separate scoped references/drafts and configured commands; the AI checks actual source before development.
- Base: blank Python 3.12/SQLite uses confirmed declarations, with no fake paths/check results.
- Bad: Vue 2 receives Vue 3 rules, a range is reported as a lock, or a driver version becomes the server version.

## 6. Tests Required

Full grouped coverage/schema/stale hashes, precise/negative manifest matching, language/runtime/driver boundaries, UI/provider routing, personal precedence/fallback, incompatible/unknown versions, package scopes, lock facts, explicit conflicts, official fetch/cache/hash/offline, immutable remote ref/subdirectory, invalid inputs, deadline/timeout, local edits and rollback. Independently copied consumers must run without the original library. Actual official HTTPS acquisition is separate from mocked boundary cases.

## 7. Wrong vs Correct

Wrong: download an unversioned guide, overwrite `.trellis/spec/`, and declare complete initialization from exit `0`.

Correct: select fixed, compatible source/ref/digest; retain local rules; acquire/cache data; generate scoped drafts and Chinese reports; inspect actual code/contracts/commands. Record semantic adaptation and tool/client verification separately. Missing candidates trigger focused primary-source research, not a claim that no standards exist anywhere.
