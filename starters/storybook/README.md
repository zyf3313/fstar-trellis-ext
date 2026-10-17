# 可复用 Storybook 评审门户

这是一个可选、可单独复制的 Storybook starter。它把项目中的产品需求说明、技术方案、共用测试用例、长期 UI 设计资产和真实可交互原型组织在同一中文侧栏中。门户是可再生投影：正文和原型数据始终从项目源文件读取，生成目录不能手工修改。

本目录自带的 `example-project/` 明确标注为示例，只用于证明 starter 可在离开原任务目录后独立安装、生成、检查和构建。

## 复制到项目

从固定版本的 Personal Trellis 仓库取出本目录，然后复制为目标项目的 `review/`：

```bash
cp -R starters/storybook /path/to/project/review
cd /path/to/project/review
pnpm install --frozen-lockfile
pnpm verify
```

普通 Trellis registry 导入只导入 `spec/`，不会自动复制、安装或运行本 starter。`node_modules/`、`storybook-static/`、日志和生成目录不属于分发内容。

## 接入真实项目

先修改 `review.config.json`：

```json
{
  "$schemaVersion": 1,
  "projectRoot": "..",
  "manifest": "review.manifest.json"
}
```

- `projectRoot` 相对于 `review/`，通常设为 `..`，表示项目根；允许使用 `..` 指向上级项目目录，但不允许绝对路径。
- `manifest` 相对于 `review/`。它只保存来源、版本、评审状态和稳定路由所需标识，不复制正文。
- `manifest` 必须留在 `review/` 内。产物 `source` 必须是相对于 `projectRoot` 的路径，且不能越出项目根。

接着修改 `review.manifest.json`，把来源映射到项目实际目录。没有既有约定时，可使用：

```text
docs/requirements/YYYY-MM-DD-slug/
  README.md
  product-requirements.md
  technical-design.md
  test-cases.md
  test-runs/<run-id>.md
design/ui/
design/prototypes/
review/
```

需求版本目录保存面向本需求的产品需求说明、技术方案、共用测试用例和运行报告。`design/ui/` 与 `design/prototypes/` 保存跨需求长期维护的设计源和原型源码；需求归档只记录不可变版本引用，不移动这些长期资产。

## Manifest 产物

默认稳定产物 ID 如下：

| ID | 默认源 | 入口 |
|---|---|---|
| `product-requirements` | `docs/requirements/YYYY-MM-DD-slug/product-requirements.md` | 产品需求说明 |
| `technical-design` | `docs/requirements/YYYY-MM-DD-slug/technical-design.md` | 技术方案 |
| `test-acceptance` | `docs/requirements/YYYY-MM-DD-slug/test-cases.md` | 测试验收 |
| `ui-design` | `design/ui/ui-design.md` | UI 设计说明 |
| `product-prototype` | `design/prototypes/product-prototype.md` | 原型说明与四个交互状态 |

`required: false` 的可选文档不存在时会被跳过，不生成空 story 或 autodocs。
`product-prototype` 是 starter 固定必需产物：manifest 缺少该 ID，或其来源缺失，
生成都会失败。其他文档可按项目评审合同调整必需性。

`ui-design` 是可选产物。manifest 不含该 ID，或它标为 `required: false` 且来源
不存在时，“共享设计资产”和“UI 设计说明”两个入口都会省略，类型检查和构建
不会引用缺失来源；来源存在时保持两个入口与来源证明。若将它标为必需，来源缺失
仍会在生成阶段失败。

普通文档入口由 manifest 的 `story` 字段驱动：

```json
{
  "story": {
    "id": "risk-review",
    "group": "文档",
    "name": "风险评审"
  }
}
```

新增或删除普通文档只需修改源文件与 manifest，不需修改生成器。`story.id` 使用稳定的小写短横线标识；`group` 选择三个既有一级组之一；`name` 使用业务名称。新增真实交互组件或新的产物渲染类型时才扩展 Storybook 源码。不要创建只有一个叶子的中间分组。

Markdown 必须包含一级标题。普通模板正文可以直接使用，不要求为了预览增加
专用元数据。需要在正文源中补充日期、截止时间或摘要时，可选用 `meta` 数据块：

````markdown
# 标题
```meta
date: 2026-10-17
review_deadline: 2026-10-24
summary: 一句话摘要
```
````

原型源还需包含 `prototype` JSON 数据块，至少提供两个状态。默认 Vue 原型使用 `draft`、`reviewing`、`changes`、`approved` 四个稳定状态 ID。

同一目录或项目根内的 Markdown 相对链接，只有在目标文件也登记于 manifest
时才会转换为对应的稳定 Storybook 路由；`#anchor` 会保留。模板使用的
`<a id="..."></a>` 安全显式锚点会渲染为页内目标，其他原始 HTML 仍按文本
转义。这样产品需求说明可链接到技术方案中的字典 `typeCode`，又不会开放任意
文件导航。

## 命令

```bash
pnpm generate
pnpm dev
pnpm build
pnpm preview
pnpm check:build
pnpm verify
```

- `generate`：读取配置、manifest 和真实源文件，校验路径，计算 SHA-256，生成 stories、运行数据和可下载的逐字节源副本。
- `dev`：生成后启动 Storybook，默认地址 `http://localhost:6106/?path=/story/dossier-home--overview`。
- `build`：生成并输出 `storybook-static/`。
- `preview`：在 `127.0.0.1:6107` 预览已有 `storybook-static/`；先运行 `pnpm build`。
- `check:build`：按当前 manifest 检查最终索引；默认示例为 3 个一级组、12 个稳定 story、0 个 autodocs、7 个阅读入口和 5 个保留工具的交互入口。
- `verify`：运行静态检查、运行时测试、类型检查、来源一致性检查、生产构建和最终索引检查。

生成器在必需来源缺失、绝对路径、目录逃逸（含符号链接）、manifest 产物或
story ID 重复、一级标题缺失、显式锚点重复、原型状态缺失或重复时失败。
默认交互入口要求原型提供 `draft`、`reviewing`、`changes`、`approved` 四个
状态；若要采用其他状态模型，需要同步修改静态 stories 与原型组件。修改源文件
后重新运行 `generate`，页面正文与 SHA-256 会同步更新。

## 显示边界

门户保留已确认的案卷视觉、三个中文一级组、无空 autodocs、稳定深链接和阅读/交互面板策略。Markdown 阅读器支持标题目录、表格、代码、列表、引用和安全 HTTP(S) 链接。

Mermaid 目前显示可复制源码与明确降级说明，不宣称已经图形渲染。PDF、图片、Office、设计源和未知格式只提供 adapter 合同与安全降级说明；接入真实查看器或转换服务时，应记录来源哈希、查看器/转换器版本和失败路径。

自动化构建不能代替真实浏览器验收。交付前仍需检查桌面与 320/375/390/430 CSS px 宽度、页面 `clientWidth`/`scrollWidth`、键盘焦点、状态播报、减少动态效果和所有深链接。
