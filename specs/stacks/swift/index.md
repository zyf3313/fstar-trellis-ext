# Swift engineering baseline

**Trigger:** The target package declares or has parsed evidence for `swift`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Expose clear value/reference and optional/error semantics. Preserve access control and protocol boundaries; avoid forced unwraps for externally supplied or lifecycle-dependent state.

- Own tasks and cancellation, identify actor isolation and UI-thread ownership, and review captured references for retain cycles. Match concurrency checks to the actual compiler mode.

- Swift tools-version and Xcode SWIFT_VERSION describe configuration, not a verified compiler. Test supported platforms and availability guards with the selected toolchain.

Source: [Official reference](https://www.swift.org/documentation/api-design-guidelines/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
