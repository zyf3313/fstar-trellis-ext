# Vue 2 compatibility baseline

**Trigger:** The target package uses major 2. Do not apply the major-3+ profile here.

- Preserve the existing Options API and the project router/store/plugin versions. Vue 2 observes properties at creation; use its supported reactive insertion/update mechanism where needed instead of assuming Vue 3 proxy behavior.

- Use the actual beforeDestroy/destroyed lifecycle for owned listener/timer/subscription cleanup and stable component/list identity. Do not apply Vue 3 composition/lifecycle or v-model contracts without an explicit migration.

- Test reactive updates, component events, route recovery and keyboard/mobile states through the legacy build. Record maintenance/EOL constraints and supported dependencies; this profile is not an upgrade authorization.

Source: [Version-specific reference](https://v2.vuejs.org/v2/guide/). Reviewed 2026-10-13. Confirm exact patch, dependencies and current maintenance policy in the project.
