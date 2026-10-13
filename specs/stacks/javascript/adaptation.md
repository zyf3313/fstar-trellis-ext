# JavaScript project adaptation

Common JavaScript contracts apply across supported runtimes; browser, Node and embedded targets remain distinct.

- Read the actual module format, runtime and bundler configuration. Follow existing imports/exports and avoid assuming browser globals or Node APIs across targets.
- Keep async errors observable and use lifecycle owners for timers/listeners/pending work. Preserve null/undefined, serialization and boundary validation behavior.
- Reuse configured lint/format/test/build scripts. Script discovery does not execute commands and does not prove that dependencies are installed.
- Prefer the project's current abstraction and naming conventions. Do not add TypeScript, a frontend framework or a runtime upgrade merely because a general guide uses one.

Version-sensitive APIs require actual runtime evidence and focused tests. This guide is not a Node-version compatibility claim.
