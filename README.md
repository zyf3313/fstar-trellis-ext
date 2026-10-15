# Personal Trellis

基于 [Trellis](https://github.com/mindfold-ai/Trellis) 的个人扩展规范库：保留 Trellis 原生任务流程，在其上增加按场景加载的指南、面向用户的中文 PRD/TDD 与 UI 模板，以及可选的工具准备入口。

普通项目通过 Trellis 原生 registry 使用本库，**不需要手工 clone**。Trellis 会读取指定的私有仓库提交并把 `personal-core` 导入目标项目；clone 只用于维护本仓库，或运行当前尚未发布为 pip/npm 包的 repository-local 包装器。

[官方 Trellis 仓库](https://github.com/mindfold-ai/Trellis) · [官方文档](https://docs.trytrellis.app/) · [Trellis Quick Start](https://docs.trytrellis.app/start/install-and-first-task) · [场景入口](spec/personal-index.md) · [变更记录](CHANGELOG.md)

> 当前状态：`1.1.0` 未公开发布候选 · 私有仓库 · 许可证待定 · 已验证 Trellis CLI `0.6.9`

## 为什么需要这层扩展

Trellis 已经提供 workflow、任务生命周期、项目规范、记忆和多平台接入。本仓库不重复这些能力，只沉淀需要在特定项目或任务中才启用的个人实践。

| 能力 | Trellis 原生负责 | Personal Trellis 增加 |
|---|---|---|
| 工作流 | 需求讨论、设计、实施、检查、归档和记忆 | 不改变原生阶段，只在语义命中时补充指南 |
| 项目规范 | `.trellis/spec/`、项目索引和本地约束 | 一页式场景入口与 7 份专项指南 |
| 产品与技术设计 | 原生 `prd.md` / `design.md` 作为 AI 任务上下文 | 面向用户评审的中文 PRD、TDD 与类型适配模板 |
| UI 设计 | 项目自行决定设计和实现方式 | 0→1 UI 基线、模块交互、可点击原型与设计一致性规则 |
| 工具使用 | 支持项目按需组合工具 | CodeGraph、QMD、GitHub/Web、DBHub、Exa、Emil Skills 的触发与边界 |
| 初始化 | `trellis init` 生成原生结构与平台资产 | 可选包装器串联固定 ref 导入、缺失工具检测和安全准备 |
| 文档一致性 | 原生任务记录和规范更新 | PRD/TDD/UI/实现/测试之间的变更传播与证据规则 |

## 与 Trellis 的边界

![Trellis 原生能力、衔接原则与 Personal Trellis 按需补充能力对照](assets/trellis-capability-comparison.png)

*图 1：Personal Trellis 只补充场景指南、中文模板与可选工具准备；原生 runtime、workflow 和项目所有权保持不变。*

Trellis 的 workflow、任务目录、代理调度、项目索引、本地规范和记忆始终由目标项目与官方 runtime 管理。本仓库只拥有 `personal-core` 内容和可选包装器，不修改、fork 或内置 Trellis runtime。

## 前置条件

- 已按 [Trellis 官方安装说明](https://docs.trytrellis.app/start/install-and-first-task) 安装 CLI；官方当前要求 Node.js 18+、Python 3.9+。
- 目标项目目录已经存在，例如 `/path/to/project`。
- 私有仓库 `zyf3313/personal-trellis` 尚未公开时，当前 Git/SSH 环境必须具有读取权限。先用自己的账号配置 SSH，不要把 token 写入 registry URL、命令历史或项目文件。
- 将示例中的 `YOUR_NAME` 替换为开发者身份，将 `<VERIFIED_COMMIT_SHA>` 替换为经过审阅的完整 40 位提交 SHA。不要直接使用会漂移的 `main`。

## Quick Start：通过原生 registry 使用

以下命令都由 Trellis 自己读取远端 registry；消费者不需要 clone 本仓库。

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

需要安装 Trellis 为 Claude Code 提供的状态栏时，在上面的命令中增加 `--with-statusline`；它默认关闭，也不影响 `personal-core` 内容。

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

`--append` 只加入缺失文件，并在 `.trellis/config.yaml` 记录 registry source 与 `personal-core` template。它不保证自动更新或合并同名文件，也不会准备工具。已有项目执行前应检查本地修改，执行后核对 workflow、配置、hooks、索引与本地规范没有被意外改变。

### 切换个人规范固定提交

先审阅旧 SHA 到新 SHA 的差异，并在隔离项目验证新提交，再执行：

```sh
cd /path/to/project
trellis init \
  --registry 'git@github.com:zyf3313/personal-trellis#<NEW_VERIFIED_COMMIT_SHA>' \
  --template personal-core \
  --append
```

这条命令可以记录新 ref 并补齐缺失文件，但不会替你覆盖或合并已经存在的同名规范。更新现有内容时，应按审阅结果逐项合并；需要回滚时，重新使用上一条已验证的完整 SHA，并恢复对应文件版本。

## 如何启用场景路由

导入后，项目只需引用一次 `.trellis/spec/personal-index.md`，不需要把全部指南写进上下文。

在项目现有规范索引中增加一条链接：

```md
- [Personal scenario index](../personal-index.md)
```

相对路径应按实际索引位置调整。也可以只为当前任务在 `implement.jsonl` 或 `check.jsonl` 加入一条：

```json
{"file":".trellis/spec/personal-index.md","reason":"Route this task to the matching personal scenario guide"}
```

项目自己的索引仍是权威入口。本库不分发 `guides/index.md`；任务先读 `personal-index.md`，再只加载语义命中的指南和必要模板。

![Trellis 原生讨论设计主干与 Personal Trellis 场景按需路由](assets/scenario-routing.png)

*图 2：个人指南、模板和工具只在命中条件时加载，并带着最小必要上下文回到原生实施与检查。*

已知的小文件直接读取，稳定的本地事实无需额外检索。工具选择、安装或发现、客户端加载、实际调用和任务验收是五个不同状态，不能用其中一个替代另一个。

## 7 份场景指南

| 场景 | 指南 | 何时触发 | 何时跳过 |
|---|---|---|---|
| 中文 PRD / TDD | [产品与技术设计](spec/guides/product-technical-design.md) | 用户明确要求；或 0→1、大型迭代、跨模块/系统、核心流程/数据/公共契约变化时，在原生设计收敛后询问一次 | 小修复、文案/样式小改、无可观察合同变化的内部重构默认不生成 |
| UI 设计与交互 | [UI 设计](spec/guides/ui-design.md) | 用户明确要求设计稿、原型、预览或平台交付；0→1 UI 且没有已确认风格时，在设计阶段询问一次是否需要完整 UI 方案 | 无 UI 影响时跳过；已有项目和小改复用现有基线，只设计受影响功能 |
| 文档一致性 | [文档一致性](spec/guides/document-consistency.md) | 已有 PRD/TDD/UI/实现/证据发生受影响变化时 | 内部实现不改变外部行为或契约时，只记录必要实现与验证结论 |
| 代码结构检索 | [代码检索](spec/guides/code-search.md) | 定义、签名、调用关系、影响范围等结构问题 | 已知小文件、字面量、注释与日志直接读文件或使用 `rg` |
| 知识与历史检索 | [知识检索](spec/guides/knowledge-search.md) | 跨文档发现、历史决定或大文档集合检索 | 单个已知文档直接读取，不为一次小查询建立索引 |
| Web / GitHub 调研 | [Web 调研](spec/guides/web-research.md) | 当前事实、官方资料核实、开源项目探索、GitHub 代码/issues 检索 | 本地证据已足够回答稳定问题时跳过 |
| 数据库访问 | [数据库访问](spec/guides/database-access.md) | schema/数据检查、SQL 验证或明确授权的数据变更 | 本地契约、迁移或 fixture 已能回答时跳过；无授权不连接、不写入 |

一个任务可以命中多个场景，但不能因此默认加载全部指南。

## 7 份中文模板

| 模板 | 用途 | 使用方式 |
|---|---|---|
| [中文 PRD](spec/templates/prd.zh-CN.md) | 项目背景、业务全景、模块职责、功能、流程与验收 | 面向用户评审；不替代 Trellis 原生 `prd.md` |
| [中文 TDD](spec/templates/technical-design.zh-CN.md) | 模块与功能实现方案、契约、数据、测试和影响 | 面向用户/研发评审；不替代原生 `design.md` |
| [TDD 类型适配](spec/templates/technical-design-profiles.zh-CN.md) | Web/API、前端/移动端、CLI/SDK、数据任务、基础设施等类型裁剪 | 与中文 TDD 组合，不机械套用前后端接口结构 |
| [UI 基线](spec/templates/ui-baseline.zh-CN.md) | 设计语言、tokens、组件、整体框架、导航和全局状态 | 0→1 或缺少基线的 UI 项目在实现前确认 |
| [功能交互设计](spec/templates/ui-feature.zh-CN.md) | 页面、模块、功能、状态、交互、异常恢复和原型 | 已有基线后，按受影响模块逐项设计 |
| [评审与变更记录](spec/templates/review-change.zh-CN.md) | 冻结版本、需求到验收映射、变更传播与证据失效 | 可并入现有方案或任务记录，避免建立第二套计划 |
| [参考项目探索](spec/templates/exploration.zh-CN.md) | 候选项目、来源、复用点、限制与选型证据 | 参考项目探索或重要选型时使用；简单事实查询不生成报告 |

模板随 `personal-core` 一起进入 `.trellis/spec/templates/`。只读取当前场景所需文件；小任务不强制生成 PRD、TDD 或整套 UI 设计。

## UI 设计约定

`emil-design-eng` 是个人规范中的唯一核心 UI 设计 Skill。以下专项仅在条件满足时追加，不与另一套核心设计方法并行主导：

| 条件 | Skill | 交付重点 |
|---|---|---|
| 新方向或一般界面/交互设计 | `emil-design-eng` | 信息架构、界面、交互和实现质量 |
| 真实数据可能撑破、为空或缺失 | `break-ui` | 空、长、缺失和边界数据状态 |
| 新增、修改或排查动效 | `review-animations` | 动效、减少动效和目标浏览器检查 |
| 手机或触摸目标 | `mobile-native` | 触摸、布局和真实设备关键路径 |

0→1 UI 项目在开发前至少确认设计语言、tokens/组件、整体框架、导航和关键交互。只有用户选择完整交付时，才继续制作全量模块画板、可点击原型和适用的 Figma、MasterGo 等设计平台交换文件。已有项目优先复用已经确认的设计系统。

## 可选：一次初始化与工具准备

`bin/trellis-personal` 是 repository-local 包装器，先调用原生 `trellis init`，再检测并准备安全的缺失工具。它当前没有发布为 pip、npm 或 uv 包，因此需要从具有读取权限的本地 checkout 执行；普通规范消费仍应使用上面的原生 registry 命令。

包装器要求 Python 3.9+，仅支持 macOS 和 Linux。原生 Trellis 参数必须放在独立的 `--` 后面。`--registry`、`--template`、`--append` 与 `--overwrite` 由包装器管理，不能再次透传。

如果确实要维护本库或运行当前 repository-local 包装器，才需要 checkout：

```sh
git clone git@github.com:zyf3313/personal-trellis.git
cd personal-trellis
git checkout '<VERIFIED_COMMIT_SHA>'
```

### 先看计划，不做修改

```sh
./bin/trellis-personal init \
  --project /path/to/project \
  --personal-ref '<VERIFIED_COMMIT_SHA>' \
  --dry-run \
  --agent codex \
  -- --codex --user YOUR_NAME
```

`--dry-run` 输出原生初始化、工具检测与准备计划，不执行外部命令，也不写报告。

### 应用到 Codex

```sh
./bin/trellis-personal init \
  --project /path/to/project \
  --personal-ref '<VERIFIED_COMMIT_SHA>' \
  --agent codex \
  -- --codex --user YOUR_NAME
```

### 应用到 Claude Code

```sh
./bin/trellis-personal init \
  --project /path/to/project \
  --personal-ref '<VERIFIED_COMMIT_SHA>' \
  --agent claude-code \
  -- --claude --user YOUR_NAME
```

Claude Code 需要 Trellis 状态栏时，可把原生参数改成 `-- --claude --with-statusline --user YOUR_NAME`。`--agent codex|claude-code` 只决定 Emil Skills 的检测与安装目录；真正生成哪些 Trellis 平台资产仍由 `--` 后的 `--codex`、`--claude` 等原生参数决定。

### 只执行原生初始化，跳过工具准备

```sh
./bin/trellis-personal init \
  --project /path/to/project \
  --personal-ref '<VERIFIED_COMMIT_SHA>' \
  --skip-tools \
  --agent codex \
  -- --codex --user YOUR_NAME
```

从来源正确的 `zyf3313/personal-trellis` checkout 运行时，可以省略 `--personal-ref`，包装器会固定当前 HEAD；其他位置必须显式传入完整 SHA。

### 初始化报告

应用模式会把脱敏报告写入：

```text
.trellis/personal/bootstrap-report.json
```

报告区分：

| 状态 | 含义 |
|---|---|
| `installed` | 本次执行后实际检测到已安装或已初始化 |
| `already_available` | 执行前已经可用，未重复安装 |
| `deferred` | 留到对应场景首次使用，不属于初始化 |
| `unsupported` | 当前平台或依赖不满足，并给出人工动作 |
| `failed` | 命令失败或执行后没有检测到预期结果 |

整体 `overall` 为 `complete`、`partial` 或 `failed`。`complete` 表示原生初始化成功且没有已执行项目失败，仍可能同时存在需要后续处理的 `deferred` 或 `unsupported` 项，应以逐项状态为准。工具失败不会回滚已经成功的 Trellis 初始化，但会返回非零并保留 partial 报告；原生初始化失败时不会继续准备工具。报告只能证明准备状态，不能证明客户端已经加载工具、账号已认证、任务已经执行或验收已经通过。

<details>
<summary><strong>包装器的检测与安装细节</strong></summary>

- CodeGraph 与 QMD 只在命令缺失时通过 npm 安装固定版本；GitHub CLI 只在 macOS 且已有 Homebrew 时自动安装，Linux 不自动执行 `sudo`。
- Emil 的缺失项使用一次 `npx -y skills@1.7.0 add emilkowalski/skills` 调用，每项追加 `--skill <name>`，最后追加 `-g -a <codex|claude-code> --yes`。随后在目标目录逐项检查 `SKILL.md`；`CODEX_HOME` 和 `CLAUDE_CONFIG_DIR` 会覆盖默认的 `~/.codex/skills` 与 `~/.claude/skills`。
- `npx` 不可用时 Emil Skills 逐项记为 `unsupported`；安装后仍缺文件的项记为 `failed`，任一工具项失败会使整体 `overall` 变为 `partial`。安装命令非零时，已经逐项检测到 `SKILL.md` 的 Skill 仍记为 `installed` 并保留非零退出信息。
- 只有可识别的代码项目且缺少 `.codegraph/` 时才运行 `codegraph init`，已有索引不会重复初始化。
- 原生命令除了退出码为零，还必须没有显式 `Error:`、实际生成 `.trellis/spec/personal-index.md`，并在 `.trellis/config.yaml` 记录匹配的固定 registry source 与 template，否则立即按失败处理。
- 报告路径经过目录、普通文件和符号链接边界检查；外部命令使用参数数组执行，命令与报告中的常见秘密字段会脱敏。

</details>

## 工具与来源

| 工具/来源 | 用途 | 初始化行为 | 按需或 deferred 边界 | 官方地址 |
|---|---|---|---|---|
| CodeGraph | 代码符号、调用关系与影响范围 | 包装器检测 CLI；缺失时固定安装 `@colbymchenry/codegraph@1.6.2`；可识别代码项目缺少 `.codegraph/` 时执行 `codegraph init` | 使用前仍检查仓库身份与索引新鲜度；已知小文件直接读取 | [GitHub](https://github.com/colbymchenry/codegraph) |
| QMD | 跨文档发现与历史决策检索 | 包装器检测 CLI；缺失时固定安装 `@tobilu/qmd@2.5.3` | collection、embed 和本地模型下载全部留到知识检索首次需要时 | [GitHub](https://github.com/tobi/qmd) |
| GitHub CLI (`gh`) | 仓库、代码、issues 和源码核实 | 已有则复用；macOS 且已有 Homebrew 时可安装；Linux 不自动提权 | `gh auth login`、账号与 scope 留到明确的 GitHub 场景 | [官网](https://cli.github.com/) · [GitHub](https://github.com/cli/cli) |
| `emil-design-eng` | UI 核心设计方法 | 缺失时通过固定 `skills@1.7.0` 安装到所选 Agent | 仅 UI 场景触发；安装不代表客户端已加载 | [Emil Skills](https://github.com/emilkowalski/skills) |
| `break-ui` | UI 数据边界检查 | 与其他缺失 Emil Skills 合并为一次安装并逐项复核 `SKILL.md` | 真实数据可能造成空、长、缺失或破版时触发 | [Emil Skills](https://github.com/emilkowalski/skills) |
| `review-animations` | 动效与可访问性检查 | 同上 | 动效新增、变化或缺陷涉及动效时触发 | [Emil Skills](https://github.com/emilkowalski/skills) |
| `mobile-native` | 移动端与触摸交互检查 | 同上 | 手机、触摸和真实设备路径时触发 | [Emil Skills](https://github.com/emilkowalski/skills) |
| DBHub | 统一的数据库 MCP 访问 | 包装器不安装、不创建连接 | 数据源、凭证、只读限制、写权限与真实连接必须在授权数据库任务中配置 | [GitHub](https://github.com/bytebase/dbhub) |
| Exa MCP | 外部研究与搜索补充 | 包装器不连接服务 | API key、账号与实际调用留到 Web 调研明确需要时 | [GitHub](https://github.com/exa-labs/exa-mcp-server) |
| [linux.do](https://linux.do/) | Web 调研可选信源 | 不是安装工具，也不属于初始化器 | 仅在用户指定或问题需要社区材料时搜索，并继续核实原始来源 | [站点](https://linux.do/) |

Google、X、GitHub、linux.do 等是可选信息来源，不代表一个必须安装的聚合工具。用户指定来源或项目已有能力时优先复用；涉及私有查询、账号、付费或写操作时先遵循对应授权边界。

## 工作原理

1. `trellis init` 从固定 Git 提交读取 `index.json`，选择 `personal-core` 并把 `spec/` 加入目标项目。
2. 项目索引或任务 JSONL 单链接引用 `personal-index.md`。
3. AI 根据当前语义只加载一到数份匹配指南。
4. 指南判断是否需要中文模板、UI Skill、代码/知识/Web/数据库工具或直接使用本地证据。
5. 原生 Trellis 继续负责设计、实施、检查与完成流程。
6. PRD/TDD/UI、实现和测试发生变化时，文档一致性指南只更新受影响的权威来源与投影，并让旧证据失效。

中文 PRD/TDD 是面向用户的附加产物，不替代 Trellis 原生 `prd.md` 和 `design.md`。大型任务在原生需求与设计收敛后、实施前询问一次；用户已经明确要求或拒绝时不重复询问。

## 仓库结构

```text
personal-trellis/
├── README.md
├── CHANGELOG.md
├── index.json                 # Trellis registry：personal-core
├── library.json               # 版本、兼容与发布状态
├── assets/                    # README 中文关系图
│   ├── trellis-capability-comparison.png
│   └── scenario-routing.png
├── bin/
│   └── trellis-personal       # 可选 repository-local 包装入口
├── bootstrap/
│   ├── __init__.py
│   ├── personal_init.py       # 原生 init、工具准备、报告与安全边界
│   └── tools.json             # 工具来源、固定版本与 deferred 声明
├── spec/
│   ├── personal-index.md      # 单入口场景路由
│   ├── guides/                # 7 份场景指南
│   │   ├── product-technical-design.md
│   │   ├── ui-design.md
│   │   ├── document-consistency.md
│   │   ├── code-search.md
│   │   ├── knowledge-search.md
│   │   ├── web-research.md
│   │   └── database-access.md
│   └── templates/             # 7 份中文模板
│       ├── prd.zh-CN.md
│       ├── technical-design.zh-CN.md
│       ├── technical-design-profiles.zh-CN.md
│       ├── ui-baseline.zh-CN.md
│       ├── ui-feature.zh-CN.md
│       ├── review-change.zh-CN.md
│       └── exploration.zh-CN.md
└── tests/
    └── test_personal_init.py
```

本库不包含个人 workflow、Trellis meta-Skill、catalog/bundle 层、UI 演示项目、Storybook 或自制发布系统。

## 更新、兼容与回滚

Trellis runtime 和个人规范 ref 是两个独立版本轴：

| 变化 | 更新方式 | 验证重点 | 回滚 |
|---|---|---|---|
| Trellis runtime | 遵循 [官方升级与变更记录](https://docs.trytrellis.app/changelog) | 原生 workflow、配置、hooks、任务、平台资产和项目索引 | 回到项目已验证的 Trellis 版本 |
| Personal Trellis | 审阅个人库两个 SHA 的差异，再以新固定 SHA 导入/合并 | 7 指南、7 模板、项目本地修改、场景路由和包装器合同 | 恢复上一已验证 SHA 与对应文件 |

当前自动化和隔离消费验证使用 Trellis CLI `0.6.9`。这说明该版本与当前提交组合通过既有检查，不构成对未来 Trellis 版本、其他操作系统、真实账号、模型、数据库或设备环境的保证。升级任一版本轴后都应重新执行适用的兼容验证。

## 安全与证据边界

- 不在 registry URL、README、初始化报告或任务记录中保存 token、DSN、密码、API key 和数据库凭证。
- 包装器不静默提权，不自动执行 GitHub 登录、数据库连接/写入、QMD 模型下载或 Exa 认证。
- 数据库默认从最小只读范围开始；任何写操作都需要明确的数据源、环境、范围和授权。
- 私有仓库访问使用当前用户已有的 Git/SSH 凭据；仓库公开前，未获权限的消费者无法导入。
- 自动化测试、环境/设备验收和用户确认分别记录。文件存在、哈希、链接通过或工具已安装，都不等于业务语义、平台表现或用户验收完成。

## Resources

| 需要 | 入口 |
|---|---|
| 安装和初始化 Trellis | [Trellis Quick Start](https://docs.trytrellis.app/start/install-and-first-task) |
| 查看 Trellis 支持的平台 | [Supported Platforms](https://docs.trytrellis.app/advanced/multi-platform) |
| 理解 Trellis 实际工作流 | [Real-World Scenarios](https://docs.trytrellis.app/start/real-world-scenarios) |
| 使用个人场景路由 | [Personal scenario index](spec/personal-index.md) |
| 了解本库版本变化 | [CHANGELOG](CHANGELOG.md) |

## FAQ

<details>
<summary><strong>使用 personal-core 之前必须 clone 这个仓库吗？</strong></summary>

不需要。原生 `trellis init --registry ... --template personal-core --append` 会自行读取远端固定提交。手工 clone 只用于维护仓库，或在当前尚未发布独立 CLI 包时运行仓库内的 `bin/trellis-personal`。

</details>

<details>
<summary><strong>为什么 registry 必须使用完整提交 SHA？</strong></summary>

完整 SHA 让规范输入可审阅、可复现、可回滚。使用会漂移的 `main` 会让同一条初始化命令在不同时间得到不同规则，不利于验收和排查。

</details>

<details>
<summary><strong>Codex 和 Claude Code 都能使用吗？</strong></summary>

可以。原生初始化分别使用 `--codex` 和 `--claude`，也可以同时传入。包装器的 `--agent codex|claude-code` 只选择 Emil Skills 的目标目录；平台资产仍由 `--` 后的原生参数控制。

</details>

<details>
<summary><strong>每个任务都会生成中文 PRD、TDD 和 UI 设计吗？</strong></summary>

不会。用户明确要求时直接触发；0→1 或大型任务在原生设计收敛后询问一次；小修复默认复用现有设计。无 UI 影响时不加载 UI 指南，无数据库语义时不连接数据库。

</details>

<details>
<summary><strong>初始化报告显示 installed 是否代表任务可以直接使用？</strong></summary>

不代表。`installed` 只证明包装器执行后检测到对应文件、命令或索引。客户端是否加载、账号是否认证、索引是否新鲜、任务是否正确调用以及结果是否验收，都要在对应场景单独确认。

</details>

<details>
<summary><strong>Trellis 升级会覆盖个人规范吗？</strong></summary>

两者分开管理。升级 Trellis runtime 时检查官方生成和管理的文件；更新个人规范时检查固定 SHA 下的 `personal-core`。发现项目本地修改时先比较再合并，不把 `--append` 当成自动升级或冲突解决机制。

</details>

<details>
<summary><strong>为什么包装器没有提供 pipx、uvx 或 npx 安装命令？</strong></summary>

当前仓库没有已验证的对应发布元数据，也没有公开 release。README 不声明尚未存在的分发方式；待后续真正打包、发布并完成独立安装验证后再补充。

</details>
