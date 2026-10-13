# PHP engineering baseline

**Trigger:** The target package declares or has parsed evidence for `php`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Use the project PHP constraint, Composer lock and autoload namespaces. Apply type/strictness conventions consistently at module boundaries; preserve exception versus return-value contracts.

- Decode request/session data before domain use, bind SQL values and keep per-request resources scoped. Long-running workers must reset retained application state between jobs.

- Validate through configured Composer scripts and target PHP extensions; test invalid inputs and worker/request failures. PHP on the assistant host does not establish consumer compatibility.

Source: [Official reference](https://www.php.net/manual/en/language.types.declarations.php). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
