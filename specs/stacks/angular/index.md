# Angular engineering baseline

**Trigger:** The target package declares or has parsed evidence for `angular`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Read angular.json workspace/project targets and tsconfig before choosing a build/test command. Preserve the installed standalone/NgModule and change-detection approach; generation defaults do not authorize migration.

- Keep injectable service ownership explicit and release subscriptions/listeners with their host lifecycle. Use stable template identity and validate reactive-form/domain conversion at the boundary.

- Test route guards, async error/loading states and templates with the configured project target. Consult exact-version APIs for signals/forms/SSR and check rendered keyboard/focus behavior.

Source: [Official reference](https://angular.dev/style-guide). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
