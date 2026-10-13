# RTK routing

**Trigger:** Command has excessive output.

Use verified RTK commands or project-native concise output. Preserve underlying command semantics/exit code, important diagnostics and test/pass/skip counts, with full raw output recoverable. Do not filter required architecture/source/protocol originals or exact diffs. Existing log wrappers save raw output before filtering; avoid filtering their summary again. CLI and hook activation are separately verified. RTK estimates/output reduction are not whole-session token or cost savings.

## Scenario: owned helper process lifetime

- **Scope:** Helper installs, index/model work and disposable MCP probes.
- **Signature:** `run(project, argv, label, env=None, timeout=600)`; `MCPClient.close()`.
- **Contract:** Explicit project cwd/PWD; raw private logs; owned process group; bounded timeout and graceful/forced termination. Interruption propagates to owned children even when a launcher exits first. Do not signal a PID solely because a lock file names it; verify current process identity.
- **Error matrix:** Nonzero → retain exit/log; timeout → terminate owned group and record failure; interruption → terminate children and propagate; skipped embedding → actual-query verification; unknown database write outcome → independent readback, no automatic retry.
- **Cases:** Good: cancel launcher and verify no descendant continues. Base: normal completion and recoverable logs. Bad: kill only the launcher and report its model/index job finished.
- **Tests:** Child and signal-ignoring grandchild interruption; actual MCP shutdown/index isolation; parent data remains byte-identical. Endpoint socket timeout alone is not a total deadline.
- **Wrong / correct:** `communicate(timeout=...)` without interruption cleanup can leave work running; preserve handlers, terminate the owned group, drain with a deadline and restore handlers. MCP shutdown uses pipe EOF to distinguish a completed child from a still-running writer.
