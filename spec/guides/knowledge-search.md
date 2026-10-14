# Knowledge search

Read a known file directly. Use QMD for discovery across project documents or old
decisions when an appropriate existing collection is available. Skip indexing for
one small file. Selection does not prove collection access, model readiness or
client loading. The optional personal initializer can install a missing QMD CLI,
but collection creation, embedding and model download remain deferred to this scenario.

## Minimum route

Start with keywords, then retrieve only the relevant window. For an existing `docs`
collection, adapt these examples to actual paths and the installed `qmd --help`:

```sh
qmd search "authentication" -c docs -n 5 --json
qmd get "docs/api-reference.md"
```

Use the returned document path or ID, not the example path. Use the installed get
command's line-window options when available, or read a bounded source window.
Read the necessary original context before interpreting a decision. Expand to
`qmd query "authentication design rationale"` only when keyword recall is insufficient
and the required local models/embeddings are already available. Return source
paths/windows, relevant excerpts and any contradictory or outdated evidence.

## Maintenance and fallback

Run `qmd update` after a relevant batch of changes or before searching stale content.
Run `qmd embed` only when embeddings are pending and semantic retrieval is needed;
keyword search does not require an embed after every Markdown edit. Do not default
to forced embedding. Model changes, collection deletion and downloads require their
own authorized integration scope. Validate Chinese retrieval quality and resource
use in the target environment. Missing collections/models or poor recall fall back
to project indexes, scoped text search and original files; report the gap.

If `.trellis/personal/bootstrap-report.json` says QMD was prepared, still inspect the
actual CLI and collection state. Never interpret CLI installation as a completed
collection, embedding, local model or retrieval-quality acceptance.

Source: [QMD commands and maintenance](https://github.com/tobi/qmd#readme).
