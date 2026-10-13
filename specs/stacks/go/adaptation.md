# Go project adaptation

Applies to Go 1.x common language/module contracts; minimum toolchain remains the project's go.mod requirement.

- Follow existing packages and ownership. Keep exported APIs small and document their contracts; use explicit errors and preserve diagnostic context.
- Use gofmt conventions and existing module dependency rules. Distinguish module roots from a go.work workspace before selecting validation scope.
- Give goroutines, channels and resources clear lifecycle owners. Propagate cancellation/deadlines through context where supported; close resources and avoid leaking workers.
- Preserve error wrapping/identity and the project's HTTP, persistence and logging adapters. Add focused behavioral tests for affected boundaries.
- Read applicable go.mod/go.sum and package source. Validate the selected packages with the project's actual commands; race checks apply when shared-state/concurrency behavior changes.

Confirm version-sensitive library/API use from the actual declared toolchain. Do not assume the assistant host's Go version is the project target.
