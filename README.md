# Personal Trellis

基于 [Trellis](https://github.com/mindfold-ai/Trellis) 的个人扩展规范库：保留
Trellis 原生任务流程，在其上增加按场景加载的指南，以及面向用户的中文
PRD、TDD 与 UI 模板。

普通项目通过 Trellis 原生 registry 使用本库，**不需要手工 clone**。Trellis
读取指定的私有仓库提交，并把 `personal-core` 中的 `spec/` 导入目标项目。

[官方 Trellis 仓库](https://github.com/mindfold-ai/Trellis) ·
[官方文档](https://docs.trytrellis.app/) ·
[Trellis Quick Start](https://docs.trytrellis.app/start/install-and-first-task) ·
[场景入口](spec/personal-index.md) · [变更记录](CHANGELOG.md)

> 当前状态：`1.2.0` 未公开发布候选 · 私有仓库 · 许可证待定 · 已验证
> Trellis CLI `0.6.9`

## 为什么需要这层扩展

Trellis 已经提供 workflow、任务生命周期、项目规范、记忆和多平台接入。
本仓库不重复这些能力，只沉淀需要在特定项目或任务中启用的个人实践。

| 能力 | Trellis 原生负责 | Personal Trellis 增加 |
|---|---|---|
| 工作流 | 需求讨论、设计、实施、检查、归档和记忆 | 不改变原生阶段，只在语义命中时补充指南 |
| 项目规范 | `.trellis/spec/`、项目索引和本地约束 | 一页式场景入口与 7 份专项指南 |
| 产品与技术设计 | 原生 `prd.md` / `design.md` 作为 AI 任务上下文 | 面向用户评审的中文 PRD、TDD 与类型适配模板 |
| UI 设计 | 项目自行决定设计和实现方式 | 0→1 UI 基线、模块交互、可点击原型与设计一致性规则 |
| 工具使用 | 支持项目按需组合工具 | 场景命中后先复用本地等价能力，不足时经用户同意由 AI 准备并验证 |
| 初始化 | `trellis init` 生成原生结构、导入 registry 内容与平台资产 | 只提供 `personal-core` 规范；不安装或配置工具 |
| 文档一致性 | 原生任务记录和规范更新 | PRD/TDD/UI/实现/测试之间的变更传播与证据规则 |

## 与 Trellis 的边界

![Trellis 原生能力、衔接原则与 Personal Trellis 按需补充能力对照](assets/trellis-capability-comparison.png)

*图 1：Personal Trellis 补充场景指南、中文模板与经确认的场景工具准备；
原生 runtime、workflow 和项目所有权保持不变。*

Trellis 的 workflow、任务目录、代理调度、项目索引、本地规范和记忆始终由
目标项目与官方 runtime 管理。本仓库只拥有 `personal-core` 内容，不修改、
fork 或内置 Trellis runtime。

## 前置条件

- 已按 [Trellis 官方安装说明](https://docs.trytrellis.app/start/install-and-first-task)
  安装 CLI；官方当前要求 Node.js 18+、Python 3.9+。
- 目标项目目录已经存在，例如 `/path/to/project`。
- 私有仓库 `zyf3313/personal-trellis` 尚未公开时，当前 Git/SSH 环境必须具有
  读取权限。不要把 token 写入 registry URL、命令历史或项目文件。
- 将示例中的 `YOUR_NAME` 替换为开发者身份，将
  `<VERIFIED_COMMIT_SHA>` 替换为经过审阅的完整 40 位提交 SHA。不要使用会
  漂移的 `main`。

## Quick Start：只使用原生 registry

以下命令都由 Trellis 自己读取远端 registry；消费者无需 clone 本仓库。

### Codex

```sh
cd /path/to/project
trellis init \
  --registry 'git@github.com:zyf3313/personal-trellis#<VERIFIED_COMMIT_SHA>' \
  --template personal-core \
  --append \
  --codex \
  --user YOUR_NAME
```

### Claude Code

```sh
cd /path/to/project
trellis init \
  --registry 'git@github.com:zyf3313/personal-trellis#<VERIFIED_COMMIT_SHA>' \
  --template personal-core \
  --append \
  --claude \
  --user YOUR_NAME
```

需要 Trellis 为 Claude Code 提供状态栏时，在命令中增加
`--with-statusline`；它默认关闭，也不影响 `personal-core` 内容。

### Codex + Claude Code

```sh
cd /path/to/project
trellis init \
  --registry 'git@github.com:zyf3313/personal-trellis#<VERIFIED_COMMIT_SHA>' \
  --template personal-core \
  --append \
  --codex \
  --claude \
  --user YOUR_NAME
```

### 只导入规范，或追加到已有 Trellis 项目

```sh
cd /path/to/project
trellis init \
  --registry 'git@github.com:zyf3313/personal-trellis#<VERIFIED_COMMIT_SHA>' \
  --template personal-core \
  --append
```

`--append` 只加入缺失文件，并在 `.trellis/config.yaml` 记录 registry source
与 `personal-core` template。它不会安装工具，也不会替你更新或合并已经
存在的同名文件。执行前检查本地修改，执行后核对 workflow、配置、hooks、
索引和本地规范。

### 切换个人规范固定提交

先审阅旧 SHA 到新 SHA 的差异，并在隔离项目验证，再执行：

```sh
cd /path/to/project
trellis init \
  --registry 'git@github.com:zyf3313/personal-trellis#<NEW_VERIFIED_COMMIT_SHA>' \
  --template personal-core \
  --append
```

需要更新已有同名内容时，按审阅结果逐项合并。回滚则恢复上一已验证 SHA
对应的文件；不要把 `--append` 当作冲突解决器。

## 如何启用场景路由

导入后，项目只需引用一次 `.trellis/spec/personal-index.md`。在项目现有规范
索引中增加一条链接：

```md
- [Personal scenario index](../personal-index.md)
```

相对路径按实际索引位置调整。也可以只为当前任务在 `implement.jsonl` 或
`check.jsonl` 加入：

```json
{"file":".trellis/spec/personal-index.md","reason":"Route this task to the matching personal scenario guide"}
```

项目自己的索引仍是权威入口。本库不分发 `guides/index.md`；任务先读
`personal-index.md`，再只加载语义命中的指南和必要模板。

![Trellis 原生讨论设计主干与 Personal Trellis 场景按需路由](assets/scenario-routing.png)

*图 2：个人指南、模板和工具只在命中条件时进入，并带着最小必要上下文
回到原生实施与检查。*

## 7 份场景指南

| 场景 | 指南 | 何时触发 | 何时跳过 |
|---|---|---|---|
| 中文 PRD / TDD | [产品与技术设计](spec/guides/product-technical-design.md) | 用户明确要求；或 0→1、大型迭代、跨模块/系统、核心流程/数据/公共契约变化时，在原生设计收敛后询问一次 | 小修复、文案/样式小改、无可观察合同变化的内部重构默认不生成 |
| UI 设计与交互 | [UI 设计](spec/guides/ui-design.md) | 用户明确要求设计稿、原型、预览或平台交付；0→1 UI 且没有已确认风格时，在设计阶段询问一次是否需要完整 UI 方案 | 无 UI 影响时跳过；已有项目和小改复用现有基线 |
| 文档一致性 | [文档一致性](spec/guides/document-consistency.md) | 已有 PRD/TDD/UI/实现/证据发生受影响变化时 | 内部实现不改变外部行为或契约时，只记录必要结论 |
| 代码结构检索 | [代码检索](spec/guides/code-search.md) | 定义、签名、调用关系、影响范围等结构问题 | 已知小文件、字面量、注释与日志直接读文件或使用 `rg` |
| 知识与历史检索 | [知识检索](spec/guides/knowledge-search.md) | 跨文档发现、历史决定或大文档集合检索 | 单个已知文档直接读取 |
| Web / GitHub 调研 | [Web 调研](spec/guides/web-research.md) | 当前事实、官方资料核实、开源项目探索、GitHub 代码/issues 检索 | 本地证据足够回答稳定问题时跳过 |
| 数据库访问 | [数据库访问](spec/guides/database-access.md) | schema/数据检查、SQL 验证或明确授权的数据变更 | 本地契约、迁移或 fixture 已能回答时跳过；无授权不连接、不写入 |

一个任务可以命中多个场景，但不能因此默认加载全部指南。

## 7 份中文模板

| 模板 | 用途 | 使用方式 |
|---|---|---|
| [中文 PRD](spec/templates/prd.zh-CN.md) | 项目背景、业务全景、模块职责、功能、流程与验收 | 面向用户评审；不替代原生 `prd.md` |
| [中文 TDD](spec/templates/technical-design.zh-CN.md) | 模块与功能实现方案、契约、数据、测试和影响 | 面向用户/研发评审；不替代原生 `design.md` |
| [TDD 类型适配](spec/templates/technical-design-profiles.zh-CN.md) | Web/API、前端/移动端、CLI/SDK、数据任务、基础设施等类型裁剪 | 与中文 TDD 组合，按项目类型裁剪 |
| [UI 基线](spec/templates/ui-baseline.zh-CN.md) | 设计语言、tokens、组件、整体框架、导航和全局状态 | 0→1 或缺少基线的 UI 项目在实现前确认 |
| [功能交互设计](spec/templates/ui-feature.zh-CN.md) | 页面、模块、功能、状态、交互、异常恢复和原型 | 已有基线后按受影响模块设计 |
| [评审与变更记录](spec/templates/review-change.zh-CN.md) | 冻结版本、需求到验收映射、变更传播与证据失效 | 并入现有方案或任务记录 |
| [参考项目探索](spec/templates/exploration.zh-CN.md) | 候选项目、来源、复用点、限制与选型证据 | 重要参考项目探索时使用 |

模板随 `personal-core` 进入 `.trellis/spec/templates/`。只读取当前场景所需
文件；小任务不强制生成 PRD、TDD 或整套 UI 设计。

## 场景内 AI 软安装

工具准备发生在任务真实命中代码、知识、UI、Web 或数据库场景之后，与
`trellis init` 无关：

1. AI 先发现当前客户端已有的 CLI、MCP、Skill、连接器和内建能力。
2. 按任务能力、权限和数据边界判断真实适用性，不能只看名称或文件存在。
3. 本地等价能力足够时直接复用；用户指定的工具优先。
4. 能力缺失或不适用时，命中指南给出筛选默认、官方来源、准确动作、作用域
   和下载、配置或外部服务影响。
5. 用户明确同意后，AI 执行该次已说明的安装或配置。
6. 随后分别验证可执行/可发现、当前客户端加载和最小真实任务。下载成功或
   配置文件存在都不等于可用。

用户拒绝、环境不支持或执行失败时，使用现有能力、手工步骤或指南中的降级
方案，并说明未覆盖范围；不重复追问同一动作。登录、API key、模型下载、
数据库凭证与连接、数据库写入和外部发布不包含在工具安装同意中，仍按对应
指南单独取得授权。

## 工具、发现与验证

下表中的 `<reviewed-version>` 必须在执行前替换为从对应官方来源核对并审阅的
明确版本；不要把占位符、浮动 tag 或省略版本的 npm 包命令直接作为安装动作。

| 工具/来源 | 本地发现与适用判断 | 缺失时的推荐动作（先获同意） | 安装后验证 | 官方地址 |
|---|---|---|---|---|
| CodeGraph | 检查 MCP/CLI、仓库身份、语言覆盖和索引新鲜度 | `npm install -g @colbymchenry/codegraph@<reviewed-version>`；Agent 配置与项目 `codegraph init` 分别说明、分别确认 | 命令/索引可发现、客户端加载、真实符号查询 | [GitHub](https://github.com/colbymchenry/codegraph) |
| QMD | 检查本地文档搜索、collection、数据边界和检索质量 | `npm install -g @tobilu/qmd@<reviewed-version>`；collection、embed、模型分别说明 | CLI/客户端可见、已知文档最小检索；语义检索单独验证 | [GitHub](https://github.com/tobi/qmd) |
| GitHub CLI (`gh`) | 优先复用现有 Web/GitHub MCP 或已认证 CLI | 按官方平台步骤；例如 macOS 的 `brew install gh` 会使用当时的 formula，执行前先展示解析到的版本 | CLI/客户端可见、最小公开仓库查询；登录与 scope 单独授权 | [官网](https://cli.github.com/) |
| Emil Skills | 检查现有设计能力能否遵循项目基线并覆盖目标状态 | 用官方 `skills@<reviewed-version>` 命令安装明确的 Skill 到明确 Agent | `SKILL.md` 可发现、客户端加载、最小真实 UI 任务 | [GitHub](https://github.com/emilkowalski/skills) |
| DBHub | 检查已有数据库 provider/MCP 的引擎、只读与凭证边界 | 在目标客户端配置已审阅版本的 `npx -y @bytebase/dbhub@<reviewed-version>` | MCP 加载；经单独授权后做最小无害 schema 查询 | [GitHub](https://github.com/bytebase/dbhub) |
| Exa MCP | 现有 Web 搜索覆盖不足时才考虑 | 按官方当前入口配置托管 MCP；例如 Codex 使用 `codex mcp add exa --url https://mcp.exa.ai/mcp`，并说明配置写入与外部查询影响 | MCP 加载；匿名范围内做最小公开查询，登录/API 与更高权限单独授权 | [GitHub](https://github.com/exa-labs/exa-mcp-server) |
| [linux.do](https://linux.do/) | 用户指定或确需社区材料时作为普通信源 | 无安装动作 | 核对访问范围，并用上游一手来源验证技术结论 | [站点](https://linux.do/) |

Google、X、GitHub、linux.do 等是可选信息来源。私有查询、账号、付费或写操作
继续遵循对应授权边界。

## UI 设计约定

`emil-design-eng` 是个人规范筛选的核心 UI 设计 Skill；本地已有的用户指定
或等价能力满足任务时直接复用。专项 Skill 只在条件命中时追加：

| 条件 | Skill | 交付重点 |
|---|---|---|
| 新方向或一般界面/交互设计 | `emil-design-eng` | 信息架构、界面、交互和实现质量 |
| 真实数据可能撑破、为空或缺失 | `break-ui` | 空、长、缺失和边界数据状态 |
| 新增、修改或排查动效 | `review-animations` | 动效、减少动效和目标浏览器检查 |
| 手机或触摸目标 | `mobile-native` | 触摸、布局和真实设备关键路径 |

0→1 UI 项目在开发前至少确认设计语言、tokens/组件、整体框架、导航和关键
交互。只有用户选择完整交付时，才制作全量模块画板、可点击原型和适用的
Figma、MasterGo 等交换文件。已有项目优先复用已确认设计系统。

## 工作原理

1. `trellis init` 从固定 Git 提交读取 `index.json`，选择 `personal-core`
   并只把 `spec/` 加入目标项目。
2. 项目索引或任务 JSONL 单链接引用 `personal-index.md`。
3. AI 根据当前语义只加载一到数份匹配指南。
4. 指南决定是否读取模板、复用本地工具、提出经确认的工具准备，或直接使用
   本地证据。
5. 原生 Trellis 继续负责设计、实施、检查与完成流程。
6. PRD/TDD/UI、实现和测试发生变化时，只更新受影响的权威来源与投影，并让
   旧证据失效。

中文 PRD/TDD 是面向用户的附加产物，不替代原生 `prd.md` 和 `design.md`。

## 仓库结构

```text
personal-trellis/
├── README.md
├── CHANGELOG.md
├── index.json                 # Trellis registry：personal-core → spec/
├── library.json               # 版本、兼容与发布状态
├── assets/
│   ├── trellis-capability-comparison.png
│   └── scenario-routing.png
└── spec/
    ├── personal-index.md      # 单入口场景路由
    ├── guides/                # 7 份场景指南
    │   ├── product-technical-design.md
    │   ├── ui-design.md
    │   ├── document-consistency.md
    │   ├── code-search.md
    │   ├── knowledge-search.md
    │   ├── web-research.md
    │   └── database-access.md
    └── templates/             # 7 份中文模板
        ├── prd.zh-CN.md
        ├── technical-design.zh-CN.md
        ├── technical-design-profiles.zh-CN.md
        ├── ui-baseline.zh-CN.md
        ├── ui-feature.zh-CN.md
        ├── review-change.zh-CN.md
        └── exploration.zh-CN.md
```

本库不包含个人 workflow、Trellis meta-Skill、工具安装脚本、UI 演示项目、
Storybook 或自制发布系统。

## 更新、兼容与回滚

Trellis runtime 和个人规范 ref 是两个独立版本轴：

| 变化 | 更新方式 | 验证重点 | 回滚 |
|---|---|---|---|
| Trellis runtime | 遵循 [官方升级与变更记录](https://docs.trytrellis.app/changelog) | 原生 workflow、配置、hooks、任务、平台资产和项目索引 | 回到项目已验证的 Trellis 版本 |
| Personal Trellis | 审阅两个 SHA 的差异，再以新固定 SHA 导入/合并 | 7 指南、7 模板、项目本地修改和场景路由 | 恢复上一已验证 SHA 与对应文件 |

当前隔离消费验证使用 Trellis CLI `0.6.9`。这不构成对未来 Trellis 版本、
其他操作系统、真实账号、模型、数据库或设备环境的保证。

## 安全与证据边界

- 不在 registry URL、README 或任务记录中保存 token、DSN、密码、API key 和
  数据库凭证。
- 数据库从最小只读范围开始；写操作需要明确数据源、环境、范围和授权。
- 私有仓库访问使用当前用户已有的 Git/SSH 凭据。
- 安装、客户端加载、最小真实调用、自动化检查、环境/设备验收和用户确认
  分别记录；其中一个通过不能替代其他状态。

## FAQ

<details>
<summary><strong>使用 personal-core 之前必须 clone 这个仓库吗？</strong></summary>

不需要。原生 `trellis init --registry ... --template personal-core --append`
会读取远端固定提交。手工 clone 只用于维护本仓库。

</details>

<details>
<summary><strong>为什么 registry 必须使用完整提交 SHA？</strong></summary>

完整 SHA 让规范输入可审阅、可复现、可回滚。使用会漂移的 `main` 会让同一
命令在不同时间得到不同规则。

</details>

<details>
<summary><strong>Codex 和 Claude Code 都能使用吗？</strong></summary>

可以。原生初始化分别使用 `--codex` 和 `--claude`，也可以同时传入。

</details>

<details>
<summary><strong>导入 personal-core 会安装 CodeGraph、QMD 或 Skills 吗？</strong></summary>

不会。它只导入 `spec/`。任务命中对应场景后，AI 先复用可用的本地等价
能力；确有缺口时说明官方来源、动作和影响，经用户同意后才准备并验证。

</details>

<details>
<summary><strong>每个任务都会生成中文 PRD、TDD 和 UI 设计吗？</strong></summary>

不会。用户明确要求时直接触发；0→1 或大型任务在原生设计收敛后询问一次；
小修复默认复用现有设计。无 UI 影响时不加载 UI 指南，无数据库语义时不
连接数据库。

</details>

<details>
<summary><strong>Trellis 升级会覆盖个人规范吗？</strong></summary>

两者分开管理。升级 Trellis runtime 时检查官方生成和管理的文件；更新个人
规范时检查固定 SHA 下的 `personal-core`。发现项目本地修改时先比较再合并。

</details>
