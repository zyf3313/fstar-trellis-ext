# Python conventions

**Trigger:** Project declares Python.

Read actual Python/runtime/package/test configuration; preserve supported versions and existing formatting/types/error/CLI contracts. Use explicit paths/subprocess argv/timeouts, avoid shell interpolation of untrusted values, keep imports free of destructive side effects and dependencies owned by the target environment. Test observable command/output/state behavior. Source: https://docs.python.org/3/ ; adapt to the project's supported version rather than the assistant host.
