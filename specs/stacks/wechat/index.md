# 微信小程序 engineering baseline

**Trigger:** The target package declares or has parsed evidence for `wechat`.

**Applicability:** Version-independent COMMON engineering guidance. Release-specific APIs/configuration and project source still require review; this profile does not certify an application runtime.

- Own page/component state, subscriptions and pending requests through load/show/hide/unload lifecycles. Keep app-level session state explicit and map server authorization errors to recovery without trusting cached identity.

- Preserve platform navigation/back-stack, setData payload boundaries and native permission/login constraints. Use supported TypeScript/JS tooling and base-library availability from the actual project settings.

- Test loading/empty/error/permission states in developer tools and on real target devices. A compileType marker identifies a mini-program project, not a tested base-library version or production release.

Source: [Official reference](https://developers.weixin.qq.com/miniprogram/dev/framework/). Reference reviewed 2026-10-13; linked pages can evolve. Use documentation for the installed release before choosing an API.
