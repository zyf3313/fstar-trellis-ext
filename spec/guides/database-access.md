# Database access

Use for schema/data inspection, SQL verification or an authorized database change.
Skip when local contracts, migrations or fixtures answer the task. Use only an
existing authorized source. Never place real DSNs or credentials in a guide, task
record or command example.

## Capability discovery and AI soft install

Honor a user-selected database tool when it fits the requested engine and boundary.
Otherwise inspect available project providers, built-in connectors, MCPs, Skills and
CLIs. Evaluate engine support, source identity, credential handling, read-only
enforcement, row/resource limits, auditability and the exact requested operation;
configuration or a matching name is not proof of a working safe connection. Reuse an
adequate authorized capability.

When no adequate equivalent exists, recommend DBHub from its
[official repository](https://github.com/bytebase/dbhub). Before changing anything,
show the reviewed version and exact client action, commonly configuring an MCP
command such as `npx -y @bytebase/dbhub@<reviewed-version>`, together with the target
client, files changed and package/process impact. Ask the user to approve installation
or client configuration. Credentials, source configuration, the first real
connection and any write permission remain separate decisions; installation approval
does not authorize them. After each explicit approval, the AI performs only that
scope and never invents or requests secrets in repository files.

Verify package/executable discovery, current-client loading after any required reload,
and a minimal real schema-listing or other harmless read against the specifically
authorized source with sensitive output redacted. A process launch or configuration
file alone is insufficient. If setup, connection or credential use is refused,
unsupported or fails, use schema files, migrations, fixtures or an already-authorized
project provider and state the missing live evidence. Do not repeat a refused request.

## Read entry

Require tool-level `readonly = true` and an explicit `max_rows` appropriate to the
task, together with a database account limited to the necessary read permissions.
Do not inherit DBHub's permissive defaults. For example, an existing source's
read tool may set `max_rows = 100`; this is a chosen output cap, not an official
default or a bound on scan cost, runtime or every SQL side effect. Review the current
engine/version's read-only behavior and use project timeout/resource controls.

Confirm environment, source, schema and requested objects before invoking schema
exploration. Then use the available read-only SQL tool, following its exposed schema,
to select named columns with narrow predicates and an engine-appropriate row limit.
Start small; redact sensitive result fields. Report source/environment identity,
query scope, result/truncation and validation gaps without returning secrets or
unnecessary rows.

## Write entry

Keep writes on a separate, least-privilege entry scoped to the user's authorized
environment, objects and operations. Reuse authorization already granted for that
scope; resolve missing scope before a dependent write. Use the project's existing
migration/review process and engine-appropriate transactions or recovery mechanism;
verify the intended change and recovery evidence. A read-only tool is not a write
workaround. Do not alter credentials or connect merely to validate this guide.

Sources: [DBHub configuration](https://github.com/bytebase/dbhub/blob/main/docs/config/toml.mdx),
[configuration examples](https://github.com/bytebase/dbhub/blob/main/dbhub.toml.example)
and [read-only advisory](https://github.com/bytebase/dbhub/security/advisories/GHSA-mwwr-p57h-56pf).
