# Errors and logs

**Trigger:** Expose errors or record operation evidence.

Keep stable user-facing errors and enough correlation/context for diagnosis. Do not expose credentials, raw sensitive data or uncontrolled stacks. Preserve actual failure and uncertainty: transport timeout does not prove provider rollback. Store full diagnostics in appropriate local evidence and return a concise result. Use the project's real logging/error contracts; do not invent a universal framework wrapper.
