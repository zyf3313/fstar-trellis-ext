# Code search

Use CodeGraph for definitions, signatures, calls and change impact when the current
project has an available, initialized index. Use `rg` for literal strings, comments
and logs; directly read a known small file. Skip graph setup for a task already
answered by local evidence. This guide does not install or initialize anything.

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
categorically unsupported. Fall back to scoped `rg` and source reads, and record the
unresolved index gap. Do not generalize one missed construct into a universal blind spot.

Follow the project's own missing-index/repair authorization rule. Wait for watcher
updates after edits; repair or rebuild only when evidence justifies it, not on a
fixed full-reindex schedule. If CodeGraph is unavailable, use focused native search
and say what structural coverage remains uncertain.

Source: [CodeGraph tool and indexing documentation](https://github.com/colbymchenry/codegraph#readme)
and [server instructions](https://github.com/colbymchenry/codegraph/blob/main/src/mcp/server-instructions.ts).
