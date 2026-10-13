# Inputs and access boundaries

**Trigger:** Request, provider or data crosses a trust boundary.

Validate at real input/identity/resource boundaries. Keep field types, null/empty values, identifiers, ownership, permission scopes and transaction semantics consistent across producer, storage and consumers. Failed identity/authorization resolution cannot widen access. Verify success, base/empty and invalid/unauthorized outcomes. Apply only where that boundary exists; project-specific identity conventions remain local.
