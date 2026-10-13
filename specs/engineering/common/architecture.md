# Ownership and architecture

**Trigger:** Implement across modules.

Locate the existing owner and public contract before adding another abstraction. Reuse behavior only when business meaning matches. Keep producer/consumer/persistence/generated-client/test changes mapped; classify every affected party. Do not bypass module ownership or couple applications to helper-tool internals. Stack rules supply actual directory/type/test patterns. Record intentional implementation gaps rather than asserting that a target contract already exists.
