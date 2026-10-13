# 本地设计预览项目骨架

基于 [Storybook](https://github.com/storybookjs/storybook) 的官方 Vue 3 + Vite 集成，提供模块/功能/状态目录、完整应用布局、可输入的功能示例、状态图、中文 PRD/TDD 和手动导入文件下载。它是可独立复制和扩展的预览工程；规范库和目标业务项目的技术栈按各自实际情况选择。

## 启动与构建

Node 22.12+；本轮使用项目工具运行时 Node 24.14.0。先复制本目录，保留 package-lock.json、src 和 public：

```sh
npm ci --registry https://registry.npmjs.org
npm run dev
```

打开终端显示的 `http://127.0.0.1:8875`。左侧目录按设计语言→应用框架→模块/功能/状态→设计文件/文档排列。点页面中的标题、新建和表单可验证实际交互；示例记录只保留在当前 story 的会话中，切换/重置恢复样例。

```sh
npm run typecheck
npm test
npm run build
npm run preview
```

`dist` 为本地可运行的静态预览站；未自动发布外网，也不向 Figma/MasterGo 上传。平台文件在 `public/design/exports/requirements.sketch`，由你下载或直接选文件手动导入；说明与损失在预览站内。

## 添加项目模块

```text
.storybook/              Storybook 的入口与目录顺序
src/design/              本轮设计源与生成 token 快照
src/foundation/          设计语言、整体框架
src/modules/requirements/一个代表性模块，两功能与八状态
src/delivery/            图稿、下载、中文文档预览
public/design/           图稿、交换文件、原型与文档快照
scripts/sync-design.mjs  先验摘要，再同步设计产物
```

1. 在 `src/modules/<module>/` 添加真实 Vue 页面/组件，以本轮 `RequirementsWorkspace.vue` 为参考。
2. 为每个功能添加 `<Feature>.stories.ts`。`title: '模块/F-编号 功能'` 决定目录，导出的 story 表达正常/空/失败/校验等状态；`parameters.personal` 记录稳定模块/功能和版本。
3. 页面使用 `src/design/tokens.css` 的 token；PRD/TDD、画板、story 与验收引用同一功能 ID。已有业务项目映射自己的组件库与权限，不把演示权限当安全边界。
4. 新设计通过自己的生成器形成与本例同结构的 manifest/产物；执行 `node scripts/sync-design.mjs /absolute/path/to/generated`。设计快照已经随工程提供，单独运行无需访问 fstar。
5. 源变更后先重新生成/校验，再同步，检查相关 story 和交互。同步会明确替换 `src/design` 与 `public/design` 下的生成快照，业务组件不会被替换。

核心示例覆盖搜索/计数/详情、错误恢复、字段校验/首错焦点、提交互斥、失败保留、取消失效与成功反馈。样例不连接数据库或真实后台，生产接入由目标项目负责。

## 上游与选择

[Storybook Vue/Vite](https://storybook.js.org/docs/get-started/frameworks/vue3-vite) 与 [目录组织](https://storybook.js.org/docs/writing-stories/naming-components-and-hierarchy) 提供目录、状态示例和隔离渲染；本项目直接使用官方包，未 fork 或复制其主仓源码。Histoire、Ladle 的比较和版本依据见 [上游调研](upstream.zh-CN.md)。依赖许可由各包保留；修改本骨架时保留相关来源记录。
