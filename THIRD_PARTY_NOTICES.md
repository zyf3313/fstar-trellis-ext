# 第三方来源与许可记录

本库许可证待定，保持私有未发布候选。工具、模型、node_modules 不随包分发。当前用途选择见 [选型台账](TOOL-SELECTION.zh-CN.md)，没有默认安装包或锁定清单。

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


## 引用边界

原生 Trellis 独立安装，候选不复制其工作流或托管技能。UI 历史工具试用不等于当前选择。Figma/MasterGo 手动导入兼容性和用户接受单独验收。公开前另做许可审阅。

## 场景指南引用

五份指南是本库维护的使用规范，仅链接一手文档，不复制第三方 Skill 正文、模型或工具源码。引用不授予其许可，也不表示已安装或已测试；接入或再分发时按实际版本另审 LICENSE/NOTICE。

- [CodeGraph](https://github.com/colbymchenry/codegraph) 与 [QMD](https://github.com/tobi/qmd)：结构/文档检索参考。
- [Emil Skills](https://github.com/emilkowalski/skills)：emil-design-eng 核心及 break-ui、review-animations、mobile-native 条件参考；[Motion](https://motion.dev/docs/performance) 性能资料。
- [DBHub](https://github.com/bytebase/dbhub)：配置与只读边界参考。
- [GitHub CLI](https://cli.github.com/manual/gh_search)、[GitHub MCP](https://github.com/github/github-mcp-server)、[Exa MCP](https://github.com/exa-labs/exa-mcp-server)：Web 调研分支参考。linux.do 为普通信源，不捆绑接入组件。

历史示例/模板中的旧工具路线仅为历史参考，当前路由以 [工具台账](TOOL-SELECTION.zh-CN.md) 与场景指南为准；不因本次文档更新卸载任何已有 Skill。
