# 可借用的 GitHub 设计预览底座

> 调研日期：2026-10-13 · 依据：官方仓库、官方文档、npm 官方版本/peerDependencies；不使用 stars 代替适配验证。

| 项目 | 可以直接借用的能力 | 本轮适配判断 |
|---|---|---|
| [Storybook](https://github.com/storybookjs/storybook) | Vue/React 等框架、目录层级、页面与组件 stories、静态构建、行为测试扩展 | 采用官方 Vue/Vite 包 10.6.2；首版用目录/状态/全页面示例和本地构建 |
| [Histoire](https://github.com/histoire-dev/histoire) | Vue story/variant、Markdown、样式隔离、目录和交互预览 | 功能匹配；npm latest 为 1.0.0-beta.1、要求 Vite ^7.3；最新无 prerelease 的 0.17.17 支持到 Vite 5，本轮保留备选 |
| [Ladle](https://github.com/tajo/ladle) | React 的 story 预览、Vite、本地服务和静态站 | React 项目可选；本轮 Vue 骨架不安装第二套渲染器 |

Storybook 的 `title` 层级用于模块→功能，story 用于页面状态；业务组件负责交互与实现参考，独立设计源负责 token/画板/交换文件。预览框架不自动生成 Figma/MasterGo 文件，也不保证最终业务实现质量。

官方文档：[Vue/Vite](https://storybook.js.org/docs/get-started/frameworks/vue3-vite)、[目录层级](https://storybook.js.org/docs/writing-stories/naming-components-and-hierarchy)、[Histoire stories](https://histoire.dev/guide/vue3/stories.html)、[Histoire 文档页](https://histoire.dev/guide/vue3/docs.html)。精确运行依赖以 package-lock.json 为准。Histoire 主分支新增 MCP 等能力属于候选资料，本轮未验证其发布包，不作为默认工具能力声明。
