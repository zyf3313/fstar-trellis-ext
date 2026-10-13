# Exported UI document verification

## 1. Scope / Trigger

Maintain when changing [build.mjs](build.mjs), [verify.mjs](verify.mjs), document projection or preview synchronization. Source PRD/TDD/review and design.json remain authoritative; generated/public copies are reproducible projections. A valid source-relative link can break after copying into a different directory.

## 2. Signatures

From this complete example directory with locked dependencies available:

```sh
node build.mjs
node verify.mjs --rebuild
node ../../apps/design-preview/scripts/sync-design.mjs
node verify.mjs --synced ../../apps/design-preview/public/design
```

`--rebuild` runs two bounded rebuilds; `--synced DIRECTORY` additionally verifies an existing synchronized export. Its directory is required and resolved against the current working directory. No credentials or environment keys are required. Success emits JSON/exit 0; assertion, input and filesystem failures exit nonzero.

## 3. Contracts

Build projects `../source/design.json` links to `../design.json` in exported docs. Generated README comes from the source README with its design link adjusted and a generated-origin notice. README participates in input/output hashes; PRD/TDD/review and design version/visual facts are unchanged. Synchronization copies every manifest output including README.

Verification checks manifest input/output hashes, source version, feature anchors, Sketch schema/Chinese readback and deterministic outputs. For every exported Markdown file, local inline links must resolve to regular files under the same export root, including after symlink resolution; external URLs and page anchors are excluded. `--synced` checks the target output bytes against the same manifest before resolving its links. This is not external-link, semantic-design, platform-import or browser/device acceptance.

## 4. Validation & Error Matrix

| Condition | Result |
|---|---|
| Self-contained generated and synchronized directories | Each passes hashes and actual local file resolution |
| Missing README/design target or changed copied output | Reject missing/stale evidence |
| Link escapes export, resolves through a symlink outside it, or targets a directory | Reject |
| `--synced` without a directory | Reject |
| Source/generator/README/input change without rebuild | Reject old hashes |
| Rebuild changes output bytes | Reject reproducibility |

## 5. Good/Base/Bad Cases

- Good: regenerate authority projections, synchronize all manifest outputs, verify both directories and independently build a copied preview Target.
- Base: link-only repair preserves design version, image/Sketch/runtime hashes and user-approval status, while refreshing affected evidence.
- Bad: hand-edit copies, check only the authority documents, or claim copied links work because their strings match.

## 6. Tests Required

Check real local target existence in both exports; independently exercise a broken-link counterexample and required-argument failure; verify two rebuilds, schema/readback and source drift rejection. Run existing preview synchronization/protection tests, typecheck and copied Target build. Preserve hashes of design/runtime/visual files and keep user/platform/browser acceptance separate.

## 7. Wrong vs Correct

Wrong: copy `docs/*.md` byte-for-byte into a new layout and retain references to source-only paths.

Correct: adjust links in the generator, include their targets in the manifest, verify real files in both exports, and regenerate from authority documents.
