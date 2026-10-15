# Code search

Use this guide for definitions, signatures, calls and change impact. Use `rg` for
literal strings, comments and logs, and directly read a known small file. Skip graph
setup when local evidence already answers the task. A tool named CodeGraph, or an
index directory that merely exists, is not proof that the current repository is
indexed and usable.

## Capability discovery and AI soft install

Honor a tool the user selected when it fits the task and its permissions are
available. Otherwise inspect the current client for an equivalent built-in symbol
index, MCP, Skill or CLI. Evaluate repository identity, language coverage, caller and
impact queries, source retrieval, freshness and access boundaries; do not decide from
the tool name or executable alone. Reuse an adequate local capability and record why
it is sufficient.

When no adequate equivalent exists, recommend CodeGraph from its
[official repository](https://github.com/colbymchenry/codegraph). Explain the exact
proposed action before changing the environment. After checking the current official
release, use an explicit reviewed version such as
`npm install -g @colbymchenry/codegraph@<reviewed-version>`; do not execute the
placeholder or an omitted/floating version. This adds a global npm executable; a
separate `codegraph install` or current per-client action can write Agent/MCP
configuration, and a separate `codegraph init` in the project creates or updates
project-local index state. Check the current official instructions and installed help,
show the exact target Agent/config files and project path, and ask the user to approve
each needed scope before running it. After approval, the AI performs only those
actions.

Verify all three layers: the executable and intended repository/index are discoverable,
the current client exposes the CodeGraph tools after any required reload, and one
small real symbol query returns source from this repository. Installation success
alone is insufficient. If installation is declined, unsupported or fails, use scoped
`rg`, language-server features and direct source reads, and state which structural
relationships remain unverified. Do not repeat the same install request after refusal.

## Minimum route

- For an area question, call `codegraph_context` with the concrete task, then one
  focused `codegraph_explore` for the relevant symbols' source.
- For a precise lookup, use `codegraph_search`; for callers/callees or impact, use
  `codegraph_callers`, `codegraph_callees` or `codegraph_impact`. Inspect the exposed
  tool schema for argument names; do not assume every client exports the same prefix.
- Return symbol names and `file:line` evidence, the affected boundary and unresolved
  coverage. Read the exact source before editing. Do not repeat a successful graph
  investigation with a repository-wide grep verification.

## Missing or surprising results

A miss is not proof of absence. Check `codegraph_status`, repository identity and
index freshness when results contradict source or omit an expected symbol. Try the
actual code identifier when a natural-language query misses; Chinese is not
categorically unsupported. Wait for watcher updates after edits. Repair or rebuild
only when evidence justifies it and the project-scope action is authorized, rather
than on a fixed full-reindex schedule.

Sources: [CodeGraph documentation](https://github.com/colbymchenry/codegraph#readme)
and [server instructions](https://github.com/colbymchenry/codegraph/blob/main/src/mcp/server-instructions.ts).
