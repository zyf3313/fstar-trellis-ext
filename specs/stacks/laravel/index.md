# Laravel engineering baseline

**Trigger:** The target package declares or has parsed evidence for `laravel`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Keep routes/controllers, application services, Eloquent models and authorization responsibilities separate according to the project. Validate input before transactions and preserve migration/schema history.

- Dispatch external side effects and queued work with deliberate commit ordering. Jobs need idempotency, retry/failure ownership and worker resource/state reset; identify the real queue backend.

- Test policy/validation failures, transaction rollback and queue delivery behavior. Cache/config/worker deployment commands and features follow the installed Laravel/PHP version, not the linked example release.

Source: [Official reference](https://laravel.com/framework/docs/12.x/queues). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
