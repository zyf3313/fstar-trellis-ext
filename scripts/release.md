# Local release command contract

## 1. Scope / Trigger

Maintain this contract when changing [release.py](release.py), the [policy](../release-policy.json), archive inventory, or candidate metadata. This command packages a complete source library or extracted release. The installed consumer library omits tests, so use its `verify` command against an archive; rebuilding requires the complete release. Python 3.9+; no network, credentials, runtime installation or remote publication.

## 2. Signatures

```sh
python3 scripts/release.py build --library LIBRARY --output OUTPUT_DIRECTORY
python3 scripts/release.py verify --archive ARCHIVE.zip
```

`--library` defaults to the directory above this script's directory. `build` requires `--output`; `verify` requires `--archive`. Internal signatures: `build(root: Path, output: Path) -> dict`, `verify(archive: Path) -> dict`. Success emits JSON/exit 0; handled validation/filesystem/archive errors exit 1; argparse usage errors exit 2. No environment keys are required.

## 3. Contracts

`library.json` supplies `name`, numeric `major.minor.patch` `version`, `publication=not_published`, `tested_trellis`, and `python`. `release-policy.json` requires `schema_version=1`, `status=local_candidate`, `license_decision=pending`, unique safe top-level `files`/`directories`, and optional safe allowlisted `required_files`.

Every declared root file is required. The current library has four categories/24 rules, no bundled stack coding files, empty default source profiles, and 53 identification entries only. Withdrawn-source receipts contain identities/digests for upgrade cleanup, not active sources or rules. When `examples` is allowed, these six source files are required independently of `required_files`: `examples/ui-module/runtime/{prototype.js,gallery.html,gallery.js,requirements.css,prototype.html,styles.css}`. Other runtime assets are forbidden. Excluded dependency/cache/private trees are skipped without traversing symlinks; allowed symlinks and non-regular assets fail. Unknown root assets are excluded. Directory allowlists admit non-forbidden descendants, so review new source files before packaging.

Output: `personal-trellis-VERSION-local-candidate.zip`, sibling `.manifest.json`, and `.zip.sha256`. ZIP members have one versioned root, sorted paths, STORE compression, fixed 1980 timestamps and ordinary 0644 modes. Manifest: schema/name/version/status/publication/license/tested_trellis/python/archive_root/archive_format plus `files[{path,bytes,sha256}]`; the manifest does not hash itself. `externally_publishable=false`. `build` JSON includes archive path/hash/file/byte counts and exclusions; `verify` returns `status=verified`, counts/hash and pending publication eligibility.

`verify` validates policy, required assets, file bytes/hashes, member paths/types, and manifest/library identity/version/publication metadata. The policy and manifest travel inside the mutable archive: consistent edits can still satisfy these checks. They do not establish origin or approved content. Compare the whole ZIP SHA256 against a trusted separately obtained digest. License choice stays pending and requires a reviewed policy/implementation change before publication.

## 4. Validation & Error Matrix

| Input/condition | Outcome |
|---|---|
| Same source bytes, different mtimes/output directories | Byte-identical ZIPs |
| Output inside an allowed source directory | Rejected |
| Unsafe/traversal/duplicate member or archive symlink/non-regular file | Rejected |
| Changed, extra or missing file versus manifest | Integrity mismatch |
| Missing declared root file or required runtime source, even with edited manifest | Rejected |
| Unsupported policy schema/status/license or duplicate allowlist | Rejected |
| Manifest/library version/publication mismatch | Rejected |
| Internally consistent but unauthorized source/policy edits | May verify; trusted external digest/review required |

## 5. Good/Base/Bad Cases

- Good: validate the complete library, build twice, compare archives, verify, compare trusted digest, then extract and exercise the helper.
- Base: local candidate with pending license; asset consumption passes while remote/platform/user gates remain separate.
- Bad: remove `runtime/prototype.js`, update manifest hashes, and expect verification to pass; required-source validation rejects it.

## 6. Tests Required

Run `python3 -m unittest discover -s tests -p test_release.py -v`. Assert deterministic bytes; excluded caches/env/unknown root assets; source/archive symlink and traversal rejection; output boundary; tampered/unmanifested content; missing declared/required assets despite consistent hashes; policy/schema/license and manifest/library metadata consistency. Final acceptance also validates native index/bundle and source links, compares every manifest row with final source bytes, and installs/detects/validates from a clean extraction with repeat/local-edit/rollback checks.

## 7. Wrong vs Correct

Wrong: treat `status=verified` or a self-consistent pending-license policy as proof of trusted origin, publication rights or real user design approval.

Correct: use verification for the stated mechanical contract, check a trusted archive digest and reviewed sources, retain `license_decision=pending`, and record real remote/UI/user acceptance separately.
