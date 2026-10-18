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

## Verified baseline

Measured 2026-10-18 on macOS arm64 (Node 24.14.0, npm 11.9.0) with
`npm install -g @tobilu/qmd@2.8.3`, after explicit user approval. Only the keyword
path was exercised; models and MCP stayed off.

| Item | Measured result |
|---|---|
| Installed release | `qmd 2.8.3 (facd35e)`; global npm executable, no Skill or MCP added |
| Current-session use | `qmd --version` worked in the installing session and from a non-login shell |
| Keyword indexing | 85 Markdown files (424,581 bytes) indexed in 0.864 s |
| Index footprint | ~1.56 MiB for that collection including config; one SQLite file |
| Model state | `content_vectors` 0, `llm_cache` 0, no `.gguf`; no model download |
| Chinese and English keywords | Expected documents returned for both; `qmd get` matched the source file |

`qmd search` uses BM25/FTS and needs no model, but it still reads an indexed
collection: `collection add` scans and indexes the chosen path immediately. Treat
collection creation as its own approval scope even when no model is involved, and
confirm the exact directories before indexing.

Query quality depends on term shape. A broad single word ranked poorly
(`projection`: 56 files, target 33rd), while a phrase ranked correctly
(`"manifest projection"`: 3 files, target 2nd). Prefer a module name plus a stable
term or phrase, and escalate to semantic retrieval only when keyword recall is
insufficient.

If semantic retrieval is later approved, budget for models separately. Upstream
default download sizes, not local measurements: embedding
`embeddinggemma-300M-Q8_0.gguf` 334 MB, reranking `qwen3-reranker-0.6b-q8_0.gguf`
639 MB, query expansion `qmd-query-expansion-1.7B-q4_k_m.gguf` 1.28 GB — roughly
2.25 GB, so reserve 3–4 GB with download headroom. Default state lives in
`~/.cache/qmd/models/`, `~/.cache/qmd/index.sqlite` and `~/.config/qmd/index.yml`;
environment variables and named indexes can relocate these. The default embedding
model has limited Chinese coverage, so a Chinese corpus may need another embedding
model whose size and quality are re-checked in the target environment. `embed`,
`query`, `vsearch`, `pull` and MCP or HTTP serving each keep their own authorization
scope; keyword search requires none of them.

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
