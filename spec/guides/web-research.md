# Web research

Use for external facts, current documentation, source verification or a requested
reference. Skip extra research when sufficient local evidence answers a stable
question. Follow user-selected sources first and keep private queries out of public
services. This guide authorizes no installation, login, purchase or account change.

## Minimum route

1. Read a known URL directly. Otherwise use existing Web search for a focused lead,
   then verify the relevant official documentation or source revision.
2. For GitHub repositories, code, issues and source verification, reuse available
   authenticated `gh` in the shell. Examples use public search terms; replace the
   repository placeholder only with an appropriate authorized repository:

   ```sh
   gh search repos "codegraph" --limit 5 --json fullName,url
   gh search code "readonly" --repo OWNER/REPO --limit 5 --json path,url
   gh search issues "readonly" --repo OWNER/REPO --limit 5 --json title,url
   gh repo view OWNER/REPO --json nameWithOwner,url,defaultBranchRef
   ```

   Follow a relevant hit to the actual file and revision; issue claims alone do not
   establish implementation behavior. Check installed command help for supported
   fields. An already-available GitHub MCP is also usable; configure only needed
   toolsets/read access in an authorized integration task. Do not assume MCP always
   has higher total cost than CLI.
3. Use Exa as a supplement when existing search lacks coverage, with a narrow query
   and bounded results. Check the actual exposed tools, account limits and access;
   do not hard-code pricing, free allowances or availability.
4. Treat linux.do as an ordinary relevant or requested source, verify technical
   claims upstream, and report access limits. Use intranet tools only where the
   project already has authorized access. Never invent a special bypass or send
   internal material to a public search engine.

## Result and fallback

Return direct evidence links, dates/revisions where material, supported conclusions
and clearly marked inference or unresolved contradictions. Bound result counts and
fields; expand only when evidence requires it. If a source or tool is unavailable,
report that limitation and use accessible primary evidence. Do not claim to have
read blocked content. Recheck changing claims and integration assumptions when
reused; preserve the user's model and client choices.

Sources: [GitHub CLI search](https://cli.github.com/manual/gh_search),
[repository metadata](https://cli.github.com/manual/gh_repo_view),
[GitHub MCP configuration](https://github.com/github/github-mcp-server)
and [Exa MCP](https://github.com/exa-labs/exa-mcp-server).
