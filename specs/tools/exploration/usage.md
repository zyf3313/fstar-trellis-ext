# External exploration routing

**Trigger:** Initialize selected research capabilities or search/read reference material.

## Selection

Apply this order: explicit user source/provider and constraints → available capabilities and valid prior evidence → one minimum provider per missing capability → bounded expansion for a material evidence gap. A source is where evidence comes from; a provider is how it is retrieved. Preserve both when specified. Another source/provider cannot fulfil an unavailable explicit requirement; record alternatives with their actual coverage and keep the requested item pending/restricted.

| Capability/source | Default route | Expand when |
|---|---|---|
| General Web search/read | Reuse available Web tools; if missing, consider Exa's minimum search/read capability | Existing coverage cannot resolve the question. General search is not Google-native evidence. |
| GitHub source verification | Reuse existing `gh` or GitHub MCP with focused read-only search/file tools | Exact source/ref/license/issues are needed; avoid another equivalent backend. |
| Google-specific search | Load a compatible provider, such as SerpApi, on demand | The user requests Google or its results are necessary for the decision. |
| linux.do | Reuse public search/read or a verified site adapter on demand | Requested or material practice evidence is missing; distinguish public indexing from site search and verify Discourse site compatibility. |
| X | Reuse a compatible channel or select an X API/xurl adapter on demand | Requested or necessary author/post evidence; verify search/read/auth, not developer-document search. |

Do not default to four-platform queries, all aggregator channels, full provider schemas or duplicate same-purpose installations. Agent Reach can select/probe needed channels; Smart Search is a candidate only when multiple provider routing is necessary. Install Agent Reach from its official repository, not the unrelated same-name PyPI package. Load only selected provider guidance, configuration and necessary tools. Adapter absence is a gap, not inferred support.

Candidate references: https://exa.ai/mcp ; https://github.com/Panniantong/Agent-Reach ; https://github.com/konbakuyomu/smartsearch . Documentation/research is not runtime integration evidence. Use current returned schemas; do not invent tool names or CLI flags.

## Query and read budget

For each decision, start with 1–3 concrete questions. Reuse applicable local docs, research and exact current URLs/refs. Use one sufficient backend per question; initially keep at most 3 relevant deduplicated candidates per question and deeply read 1–2. These are adjustable starting budgets: explicit broader/deeper requests and necessary evidence override them. Record a material gap and bounded expansion before proceeding within existing authorization.

Return titles/URLs/refs and short fit summaries first, then read focused originals and exact source files. Deduplicate URLs/project revisions and avoid repeated full pages or re-querying resolved decisions. Verify needed capability, exact revision, license, fit/maintenance and limitations; distinguish README claims, original/source verification and actual trials. Stop when the decision is resolved or additional results repeat; stop unchanged unreachable-source retries after bounded failure handling. Zero results mean absence only within the recorded queries/sources/time range.

## Selected scope and runtime evidence

Record `selection_state=selected|not_requested` with reason. `not_requested` is applicability: do not handshake/install/load those special sources or count them as passed, failed or awaiting authentication. For selected items record configuration, connection, authentication, search and original-read checks separately as `passed|failed|pending|skipped`, plus coverage/restrictions. Missing required authentication is pending; public alternatives do not clear that gap. An explicit all-four request selects all four. Declare completion only for the selected scope.

Reuse compatible installations and healthy prior evidence; fill only missing selected capabilities, preserving local configs. Verify identity/version/ref or remote endpoint/date, handshake/schema, a representative query and its actual target original/source. Keep credential references local. Record auth/403/429/unreadable/truncated/empty-result limits; do not bypass access controls, acquire cookies or purchase subscriptions implicitly. Use public queries without private project material.

Prefer native toolset filters or actually verified client lazy loading. Observe the actual loaded tool count/scope; report `unknown` when unavailable. Installed configuration does not prove client loading or effective filtering. If the client lacks an adapter/filter, record the gap and context cost or choose a compatible provider within the request. Rules do not implement client lazy loading; do not promise a fixed token-saving ratio.

The Chinese report records explicit requests/constraints, selected source/provider and reuse reasons, budgets/expansion/stop conditions, evidence URL/ref/date and runtime limits. Provider/client mechanics belong in adapters. CodeGraph/RTK/QMD remain the local baseline; conditional database/UI profiles retain their own rules.
