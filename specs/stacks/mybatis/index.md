# MyBatis engineering baseline

**Trigger:** The target package declares or has parsed evidence for `mybatis`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Keep mapper interfaces, XML statement IDs, result maps and parameter objects aligned. Bind values through parameter placeholders; raw substitution for identifiers requires an explicit reviewed allowlist.

- Use the actual SqlSession/transaction integration owner and review batch flush/update counts before interpreting success. Preserve null/type-handler behavior and do not introduce a second session factory incidentally.

- Test executable SQL/result mapping against the chosen dialect and verify pagination/concurrency/error behavior. XML parsing alone does not prove queries or transaction boundaries are correct.

Source: [Official reference](https://mybatis.org/mybatis-3/sqlmap-xml.html). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
