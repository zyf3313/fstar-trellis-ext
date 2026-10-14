# Database access

Use for schema/data inspection, SQL verification or an authorized database change.
Skip when local contracts or fixtures answer the task. DBHub is the selected optional
access tool; configuration is not evidence of a successful connection or safe query.
Use only an existing authorized source. Never place real DSNs or credentials here.

The personal initializer deliberately defers DBHub runtime/source configuration,
credentials and write scope. Its report can record that boundary but never proves a
connection. Prepare DBHub only after this scenario identifies an authorized source,
environment and read/write boundary.

## Read entry

Require tool-level `readonly = true` and an explicit `max_rows` appropriate to the
task, together with a database account limited to the necessary read permissions.
Do not inherit DBHub's permissive defaults. For example, an existing source's
read tool may set `max_rows = 100`; this is a chosen output cap, not an official
default or a bound on scan cost, runtime or every SQL side effect. Review the current
engine/version's read-only behavior and use project timeout/resource controls.

Confirm environment, source, schema and requested objects before invoking the
available schema-exploration tool. Then use the existing read-only SQL tool, following
its exposed schema, to select named columns with narrow predicates and an
engine-appropriate row limit. Start small; redact sensitive result fields. Report
source/environment identity, query scope, result/truncation and validation gaps
without returning secrets or unnecessary rows.

## Write entry and fallback

Keep writes on a separate, least-privilege entry scoped to the user's authorized
environment, objects and operations. Reuse authorization already granted for that
scope; resolve missing scope before a dependent write. Use the project's existing
migration/review process and engine-appropriate transactions or recovery mechanism;
verify the intended change and recovery evidence. A read-only tool is not a write
workaround. Do not alter credentials or connect merely to validate this guide.

If DBHub or the source is unavailable, use an already-authorized project provider,
schema files or fixtures and state the missing live evidence. Recheck permissions,
read-only semantics and limits when source, engine, version or operation changes.
Integration and isolated database tests belong to an explicit connection task.

Sources: [DBHub configuration](https://github.com/bytebase/dbhub/blob/main/docs/config/toml.mdx),
[configuration examples](https://github.com/bytebase/dbhub/blob/main/dbhub.toml.example)
and [read-only advisory](https://github.com/bytebase/dbhub/security/advisories/GHSA-mwwr-p57h-56pf).
