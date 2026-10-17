# Web research

Use for external facts, current documentation, source verification or a requested
reference. Skip extra research when sufficient local evidence answers a stable
question. Follow a user-selected source or tool first when it fits the task, and keep
private queries out of public services.

## Capability discovery and AI soft install

Inspect the current client for built-in Web access, authorized connectors or MCPs,
and local CLIs such as `gh`. Evaluate source coverage, recency, primary-source access,
private-data boundary, authentication scope and result limits rather than name-only
presence. Reuse an adequate capability and record the source/revision checked.

For GitHub work without an adequate equivalent, recommend GitHub CLI from its
[official site](https://cli.github.com/) and show the platform-specific official
action before running it, such as `brew install gh` on a Homebrew-managed macOS host.
Show the package version that the manager currently resolves before requesting
approval; do not present the action as a permanently fixed version. The install adds
a local CLI; `gh auth login`, account selection and scopes are separate actions that
require their own explicit authorization. For broader search
that existing Web tools cannot cover, recommend [Exa MCP](https://github.com/exa-labs/exa-mcp-server)
through the official current hosted endpoint or supported client plugin. Show the
exact client configuration and files changed; for example, Codex currently documents
`codex mcp add exa --url https://mcp.exa.ai/mcp`. Explain that queries are sent to an
external service. Recheck the official entry point before execution. Anonymous access,
OAuth/account login, API keys, higher limits and paid features are separate scopes.

Ask the user before any installation, client configuration, login or paid/account
change. After approval, the AI performs only the approved action. Verify the
executable or MCP discovery, current-client loading after any required reload, and a
minimal public repository lookup or public Web query. If installation or account
setup is refused, unsupported or fails, use available built-in search, direct URLs
and accessible primary sources; state inaccessible coverage and do not claim to have
read blocked content or repeat a refused request.

## Minimum route

1. Read a known URL directly. Otherwise use existing Web search for a focused lead,
   then verify the relevant official documentation or source revision.
2. For GitHub repositories, code, issues and source verification, reuse available
   authenticated `gh` or an authorized GitHub MCP:

   ```sh
   gh search repos "codegraph" --limit 5 --json fullName,url
   gh search code "readonly" --repo OWNER/REPO --limit 5 --json path,url
   gh search issues "readonly" --repo OWNER/REPO --limit 5 --json title,url
   gh repo view OWNER/REPO --json nameWithOwner,url,defaultBranchRef
   ```

   Follow a relevant hit to the actual file and revision. Issue claims alone do not
   establish implementation behavior. Check installed command help for supported
   fields and use only an authorized repository.
3. Use Exa only as a supplement when existing search lacks coverage, with a narrow
   query and bounded results. Check actual tools, limits and access; do not hard-code
   pricing, allowances or availability.
4. Treat linux.do and other relevant forums or community discussions as both
   discovery sources and possible post-shortlist selection evidence. Verify technical
   claims upstream and report access limits. Use intranet tools only with existing
   authorized access. Never send internal material to a public search engine.
5. For reference-project exploration or consequential selection, inspect source at
   an exact release/ref and use the [exploration template](../templates/exploration.zh-CN.md).
   Record version, license, maintenance evidence, verified capability, adaptation
   gaps and the adopt/adapt/reject decision. A simple fact lookup needs no report.

## Community evidence after shortlisting

When two or more plausible candidates remain, or a decision is consequential or
experience-sensitive, run one bounded second pass across relevant Web and community
sources. Include linux.do when relevant or requested, and consider GitHub issues or
discussions, vendor-independent comparisons and other communities with real use
experience. Use multiple independent sources where feasible; do not count reposts or
unsourced summaries as independent confirmation.

Keep firsthand anecdotes and popularity signals separate from verified functionality.
Use community evidence to examine failure modes, migration and maintenance cost,
ecosystem fit and operational surprises; verify technical capabilities, license and
version claims against upstream documentation, source or an exact release. Record the
evidence date, likely recency and representativeness limits, source relationships and
material conflicts. Forum consensus is a lead or experience signal, not proof.

Stop when the decision is supported and additional sources repeat existing evidence or
no longer change the ranking. Record whether the second pass changed or did not change
each adopt/adapt/reject decision, with the evidence and remaining uncertainty. Do not
expand a routine fact lookup into this pass.

## Result

Return direct evidence links, dates/revisions where material, supported conclusions
and clearly marked inference or unresolved contradictions. Bound result counts and
fields; expand only when evidence requires it. Recheck changing claims when reused,
and preserve the user's model and client choices. For selection work, include the
community-evidence effect on the final ranking even when it made no change.

Sources: [GitHub CLI search](https://cli.github.com/manual/gh_search),
[repository metadata](https://cli.github.com/manual/gh_repo_view),
[GitHub MCP configuration](https://github.com/github/github-mcp-server)
and [Exa MCP](https://github.com/exa-labs/exa-mcp-server).
