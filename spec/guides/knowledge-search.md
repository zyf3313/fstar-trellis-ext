# Knowledge search

Read a known file directly. Use a document-search capability for discovery across
project documents or old decisions. Skip indexing for one small file. An executable,
collection name or configuration file does not prove collection access, model
readiness, retrieval quality or client loading.

## Capability discovery and AI soft install

Honor a user-selected tool when it fits the task. Otherwise inspect available
built-in search, MCPs, Skills and CLIs for keyword search, bounded retrieval, source
paths, collection freshness and the required local-data boundary. Reuse an adequate
equivalent and record the selected collection and why it is sufficient; do not choose
QMD from name-only presence.

When no adequate equivalent exists, recommend QMD from its
[official repository](https://github.com/tobi/qmd). Explain the exact action and
impact before changing the environment. After checking the current official release,
use an explicit reviewed version such as
`npm install -g @tobilu/qmd@<reviewed-version>`; do not execute the placeholder or an
omitted/floating version. This adds a global npm executable. Collection creation
writes local index state; semantic querying or embedding may download local models
and consume additional storage and compute. Show each needed collection, embed or
model action separately and ask the user to approve that exact scope. After approval,
the AI runs only the approved actions.

Verify the executable or MCP is discoverable, the current client can load the
capability after any required reload, and one minimal real query retrieves a known
project document with the correct source path. Verify semantic retrieval separately
when it is required. If installation, indexing or a model download is refused,
unsupported or fails, fall back to project indexes, scoped text search and original
files, and report the coverage or recall gap without asking again for the refused
action.

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
and the required local models/embeddings are available. Return source paths/windows,
relevant excerpts and contradictory or outdated evidence.

## Maintenance

Run `qmd update` after a relevant batch of changes or before searching stale content.
Run `qmd embed` only when embeddings are pending and semantic retrieval is needed;
keyword search does not require an embed after every Markdown edit. Do not default
to forced embedding. Model changes, collection deletion and downloads keep their own
authorization scope. Validate Chinese retrieval quality and resource use in the
target environment.

Source: [QMD commands and maintenance](https://github.com/tobi/qmd#readme).
