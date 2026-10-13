# Supervised Trellis execution

**Trigger:** Implementation/check dispatch or independent exploration.

The main agent owns requirements, design decisions, dispatch, progress, integration and final acceptance. In Trellis dispatch mode, use `trellis-implement` for approved implementation, then a separate `trellis-check` for review/fixes. Start the prompt with `Active task: <task path>`; assign exact file ownership, dependencies, checks and a bounded reporting deadline. Execution agents read the curated role manifest, current task artifacts, applicable project rules and exact code before work. They preserve other edits, report changes/validation/gaps and do not recursively dispatch implement/check roles. The main agent inspects consequential results and final affected-scope evidence.

Keep the main session available for user questions. Independent exploration may run alongside an execution agent when scopes do not overlap; changes to scope or shared contracts must be coordinated explicitly. Do not take over files assigned to a running agent. Use one-shot read-only scouts for focused research with source anchors, coverage and omissions; do not repeat delegated searches. Read foundational architecture/design documents in the main agent. Preserve user-selected model settings.

Respect the target project's actual dispatch mode and platform capabilities. Default to native Trellis dispatch where available; an explicit `inline` policy or active runtime restriction requires main-session execution and disclosure of that deviation. Installing these rules does not silently rewrite an existing project's config or collaboration policy. If they conflict, reconcile them before claiming dispatch readiness.
