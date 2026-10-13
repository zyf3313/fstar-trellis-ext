# 第三方来源与许可记录

本库许可证尚未选择；本地候选不代表对外分发许可。此账本不为本库指定许可证，也不替代发布前的完整许可审阅。第三方工具二进制、模型与 node_modules 不随候选交付。

## 固定的官方文档来源

身份、commit、内容/许可摘要来自 [official-sources.lock.json](official-sources.lock.json)。随包是适配规则与引用；官方资料按需下载，完整缓存不分发。不从项目名称推定许可类型。

| profile | 固定 ref | 原文 | 许可/归属入口 |
|---|---|---|---|
| official.react.common | `046f17d04295ba047bb5739026b4ac3110f17028` | [固定源码](https://raw.githubusercontent.com/reactjs/react.dev/046f17d04295ba047bb5739026b4ac3110f17028/src/content/learn/thinking-in-react.md) | [锁定许可入口](https://raw.githubusercontent.com/reactjs/react.dev/046f17d04295ba047bb5739026b4ac3110f17028/LICENSE-DOCS.md) |
| official.go.common | `575a6925e2d55ad160ed77f402bfaa4ec7458749` | [固定源码](https://raw.githubusercontent.com/golang/website/575a6925e2d55ad160ed77f402bfaa4ec7458749/_content/doc/effective_go.html) | [锁定许可入口](https://raw.githubusercontent.com/golang/website/575a6925e2d55ad160ed77f402bfaa4ec7458749/LICENSE) |
| official.rust.common | `1500248d8f230566e4ec9f27fcbb8fe9e2898ab1` | [固定源码](https://raw.githubusercontent.com/rust-lang/book/1500248d8f230566e4ec9f27fcbb8fe9e2898ab1/src/ch04-01-what-is-ownership.md) | [锁定许可入口](https://raw.githubusercontent.com/rust-lang/book/1500248d8f230566e4ec9f27fcbb8fe9e2898ab1/LICENSE-MIT) |
| official.javascript.common | `19370346042efad9e179fbf1f55deeeadee98c40` | [固定源码](https://raw.githubusercontent.com/mdn/content/19370346042efad9e179fbf1f55deeeadee98c40/files/en-us/web/javascript/guide/index.md) | [锁定许可入口](https://raw.githubusercontent.com/mdn/content/19370346042efad9e179fbf1f55deeeadee98c40/LICENSE.md) |
| official.python.common | `193d435ad52b993d7ab2b133d543dd6b78fbcfbd` | [固定源码](https://raw.githubusercontent.com/python/peps/193d435ad52b993d7ab2b133d543dd6b78fbcfbd/peps/pep-0008.rst) | [锁定许可入口](https://raw.githubusercontent.com/python/peps/193d435ad52b993d7ab2b133d543dd6b78fbcfbd/peps/pep-0008.rst) |
| official.typescript.common | `6556b08756b766fd41d0f887174cb0b042e5f72c` | [固定源码](https://raw.githubusercontent.com/microsoft/TypeScript-Website/6556b08756b766fd41d0f887174cb0b042e5f72c/packages/documentation/copy/en/handbook-v2/Everyday%20Types.md) | [锁定许可入口](https://raw.githubusercontent.com/microsoft/TypeScript-Website/6556b08756b766fd41d0f887174cb0b042e5f72c/LICENSE) |
| official.vue.common | `40aa88af0094f7bab4aaf786e55c748a6a251d88` | [固定源码](https://raw.githubusercontent.com/vuejs/docs/40aa88af0094f7bab4aaf786e55c748a6a251d88/src/guide/introduction.md) | [锁定许可入口](https://raw.githubusercontent.com/vuejs/docs/40aa88af0094f7bab4aaf786e55c748a6a251d88/LICENSE) |

## 安装时下载的工具

身份与版本以 [tools.lock.json](tools.lock.json) 为准。provider 安装时获取软件及原有许可；候选只带 adapter/helper 和锁定信息。2026-10-13 核对的默认分支许可不冒充固定发布包许可已验收。

| 工具 / 包 | 版本 / ref | 官方来源 | 许可入口与证据 |
|---|---|---|---|
| codegraph / `@colbymchenry/codegraph` | 0.9.3 / 锁定包版本，无源码 ref | [官方项目](https://github.com/colbymchenry/codegraph) | [核对入口](https://raw.githubusercontent.com/colbymchenry/codegraph/main/LICENSE)；MIT；默认分支原文核对，0.9.3 包许可另核对 |
| rtk / `rtk` | 0.51.0 / 锁定包版本，无源码 ref | [官方项目](https://github.com/rtk-ai/rtk) | [核对入口](https://raw.githubusercontent.com/rtk-ai/rtk/v0.51.0/LICENSE)；Apache-2.0；v0.51.0 原文核对 |
| qmd / `@tobilu/qmd` | 2.8.3 / 锁定包版本，无源码 ref | [官方项目](https://github.com/tobi/qmd) | [核对入口](https://raw.githubusercontent.com/tobi/qmd/main/LICENSE)；MIT；默认分支原文核对，2.8.3 包许可另核对 |
| impeccable / `impeccable` | 4.5.2 / 245ad82def45831dc56a21b683c7a1ff530b06cc | [官方项目](https://github.com/pbakaus/impeccable) | [核对入口](https://raw.githubusercontent.com/pbakaus/impeccable/245ad82def45831dc56a21b683c7a1ff530b06cc/LICENSE)；Apache-2.0；锁文件既有记录 |
| ui-ux-pro-max / `ui-ux-pro-max-cli` | 2.15.0 / 7246805992a42b7bba37d4cac83b01416f0c6c44 | [官方项目](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | [核对入口](https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/7246805992a42b7bba37d4cac83b01416f0c6c44/LICENSE)；MIT；锁文件既有记录 |
| dbhub / `@bytebase/dbhub` | 1.5.0 / 锁定包版本，无源码 ref | [官方项目](https://github.com/bytebase/dbhub) | [核对入口](https://github.com/bytebase/dbhub)；固定版本许可原文待核对；失败读取不推定许可 |

## 预览与交换示例依赖

候选含自己维护的 Vue/Storybook 预览源、设计示例和 npm 锁文件；依赖在 npm ci 时下载。直接依赖许可字段来自 package-lock.json；SPDX 链接说明许可文本，包的 LICENSE/NOTICE 以下载包为准。完整传递包 identity/version/resolved/integrity/license 保留在各锁文件，不复制 node_modules 形成另一份源码或许可库。未来分发预构建 dist 或依赖时，重新收集完整随包 LICENSE/NOTICE 并审阅。

| 使用方 / 包 | 锁定版本 | 来源包 | 锁文件许可 / 许可文本 |
|---|---|---|---|
| apps/design-preview / `@storybook/vue3-vite` | 10.6.2 | [锁定 npm 包](https://registry.npmjs.org/@storybook/vue3-vite/-/vue3-vite-10.6.2.tgz) | [MIT](https://spdx.org/licenses/MIT.html) |
| apps/design-preview / `@vitejs/plugin-vue` | 6.0.10 | [锁定 npm 包](https://registry.npmjs.org/@vitejs/plugin-vue/-/plugin-vue-6.0.10.tgz) | [MIT](https://spdx.org/licenses/MIT.html) |
| apps/design-preview / `dompurify` | 3.3.3 | [锁定 npm 包](https://registry.npmjs.org/dompurify/-/dompurify-3.3.3.tgz) | [(MPL-2.0 OR Apache-2.0)](https://spdx.org/licenses/) |
| apps/design-preview / `marked` | 17.0.5 | [锁定 npm 包](https://registry.npmjs.org/marked/-/marked-17.0.5.tgz) | [MIT](https://spdx.org/licenses/MIT.html) |
| apps/design-preview / `mermaid` | 10.9.1 | [锁定 npm 包](https://registry.npmjs.org/mermaid/-/mermaid-10.9.1.tgz) | [MIT](https://spdx.org/licenses/MIT.html) |
| apps/design-preview / `storybook` | 10.6.2 | [锁定 npm 包](https://registry.npmjs.org/storybook/-/storybook-10.6.2.tgz) | [MIT](https://spdx.org/licenses/MIT.html) |
| apps/design-preview / `typescript` | 6.0.3 | [锁定 npm 包](https://registry.npmjs.org/typescript/-/typescript-6.0.3.tgz) | [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) |
| apps/design-preview / `vite` | 8.3.4 | [锁定 npm 包](https://registry.npmjs.org/vite/-/vite-8.3.4.tgz) | [MIT](https://spdx.org/licenses/MIT.html) |
| apps/design-preview / `vue` | 3.5.43 | [锁定 npm 包](https://registry.npmjs.org/vue/-/vue-3.5.43.tgz) | [MIT](https://spdx.org/licenses/MIT.html) |
| apps/design-preview / `vue-tsc` | 3.2.8 | [锁定 npm 包](https://registry.npmjs.org/vue-tsc/-/vue-tsc-3.2.8.tgz) | [MIT](https://spdx.org/licenses/MIT.html) |
| examples/ui-module / `@sketch-hq/sketch-file-format` | 6.5.0 | [锁定 npm 包](https://registry.npmjs.org/@sketch-hq/sketch-file-format/-/sketch-file-format-6.5.0.tgz) | [MIT](https://spdx.org/licenses/MIT.html) |
| examples/ui-module / `ajv` | 8.17.1 | [锁定 npm 包](https://registry.npmjs.org/ajv/-/ajv-8.17.1.tgz) | [MIT](https://spdx.org/licenses/MIT.html) |
| examples/ui-module / `jszip` | 3.10.2 | [锁定 npm 包](https://registry.npmjs.org/jszip/-/jszip-3.10.2.tgz) | [(MIT OR GPL-3.0-or-later)](https://spdx.org/licenses/) |
| examples/ui-module / `sketch-constructor` | 1.26.0 | [锁定 npm 包](https://registry.npmjs.org/sketch-constructor/-/sketch-constructor-1.26.0.tgz) | [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) |

## 引用与随包内容边界

技术栈规范的官方链接是工程依据，不表示复制整个项目。工作流沿用 Trellis 固定标题/Phase Index 结构；原生 CLI 单独安装，官方 [mindfold-ai/Trellis](https://github.com/mindfold-ai/Trellis) 发布包许可另核对。Figma/MasterGo 的名称与导入兼容性不是本库授权，真实平台反馈单列。获取到的完整文档/许可缓存、工具凭证和消费项目设计不分发。
