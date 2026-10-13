# 个人 Trellis 规范库

目标：跨项目复用开发行为，让 AI 先探索、设计，再依据确认的 PRD/TDD/UI 稳定实现和交付。

当前是 **v1.0.0 本地发布候选**，`library.json` 保持 `1.0.0 / not_published`，库许可证待选择。**`zyf3313/personal-trellis` 私有 GitHub 源库已建立并同步**；Trellis 0.6.9 的固定提交 SSH spec/workflow 获取已实测。私有源码同步与正式发布分别记录，首次组合初始化的索引候选需明确处理，范围见 [交付与完整性说明](DISTRIBUTION.zh-CN.md)。[变更记录](CHANGELOG.md)和[第三方来源说明](THIRD_PARTY_NOTICES.md)随包提供。

## 分类
`specs/core` 管通用行为，`process` 管生命周期，`engineering` 管跨栈工程，`stacks` 管具体语言/框架/数据库，`tools` 管能力场景。每条规则有唯一 ID、触发条件、来源与目标落位。`catalog.json` 是个人引导输入，`index.json` 是 Trellis 原生 marketplace。工作流、技能、中文模板及 adapter 独立维护；bundle 从唯一源生成。

## 本地安装与使用
运行需要 Python 3.9+；Trellis 和辅助工具单独安装。先在目标项目初始化原生 Trellis，再安装本包：
```sh
trellis init --codex -u YOUR_NAME -y --skip-existing
python3 /path/to/personal-trellis/scripts/personal.py install --project /path/to/project --adopt-workflow
```
`--adopt-workflow` 表示明确选择个人工作流，先保存原文件用于回滚。省略时已有未受本包管理的 workflow 保留，生成候选 `.new.<hash>`；其他本地改动同样保留。只安装本包资产不代表工具/索引/数据库初始化完成。

空白项目先讨论并声明 `--stacks`；已有项目从真实构建配置识别，多个包组合。真实 UI 栈自动加载界面工程/设计工具规则；空白项目可用 `--capabilities ui` 声明；数据库依赖被识别或显式声明数据库栈时，使用数据库能力规则。没有命中的技术栈依据官方准确版本补充，不将通用原则冒充完整栈规范。

```sh
python3 scripts/personal.py detect --project /path/to/project
python3 scripts/personal.py build
python3 scripts/personal.py validate
python3 .trellis/personal/personal.py rollback --revision REVISION
```
安装后的脚本及资源在项目内运行，不依赖本库原目录或维护者电脑。备份/运行配置属于消费项目，不上传规范库。中文模板在 `.trellis/personal/templates`，主入口为 `.trellis/spec/guides/personal/index.md` 和三个个人 skills。

需要本地样式预览时，可选安装独立的 [Storybook 预览项目骨架](apps/design-preview/README.md)：

```sh
python3 scripts/personal.py install --project /path/to/project --capabilities ui --preview-scaffold design/preview
cd /path/to/project/design/preview
npm ci --registry https://registry.npmjs.org
npm run dev
```

它按设计语言、整体框架、模块/功能/状态组织真实 Vue 示例和图稿，提供 PRD/TDD 预览及手动导入文件下载。新增模块写在 `src/modules/`；预览依赖不替业务项目选型，栈检测会排除本工具登记的预览目录。本地修改仍由安装器保护，更新生成候选，支持回滚。

## 私有源库的固定提交消费

源库为 `zyf3313/personal-trellis`，保持 private。前提是现有 GitHub SSH 身份有该仓库读取权限；复用现有认证，不将令牌写入 URL、文档或配置，不修改全局 Git/SSH 配置。Trellis 0.6.9 的 GitHub HTTP registry index 不携带认证，`gh:` 来源加 `GIGET_AUTH` 不能补齐这个阶段；以下 SSH source 强制使用 Git backend。

将 `FIXED_COMMIT` 替换为已推送并核验的完整提交 SHA，再在独立目标执行。文档保留占位，实际 SHA 记入消费记录，避免文档提交自引用；当前命令是验收入口，不是已通过记录：

```sh
trellis init --registry 'git@github.com:zyf3313/personal-trellis#FIXED_COMMIT' --template personal-core --append
trellis workflow --template chinese-design-first --marketplace 'git@github.com:zyf3313/personal-trellis#FIXED_COMMIT' --create-new
```

`--append` 只补缺失 spec，不合并升级；`--create-new` 总是写入 `.trellis/workflow.md.new`，保留当前工作流与其 hash 记录，无论当前工作流是否修改。先比较候选，再决定是否采用；省略此参数时，未修改的工作流可以直接安装，本地修改则需显式处理。认证/错误与验证合同见 [私有 registry adapter](adapters/registry/README.md)。规范/工作流下载不隐式安装 helper、技能、模板或工具。配套资源从同一已核验提交的本地克隆目录安装：

```sh
git clone --no-checkout git@github.com:zyf3313/personal-trellis.git /path/to/personal-trellis
git -C /path/to/personal-trellis checkout --detach FIXED_COMMIT
git -C /path/to/personal-trellis rev-parse HEAD
python3 /path/to/personal-trellis/scripts/personal.py install --project /path/to/project --stack-registry /path/to/personal-trellis/stack-sources.json
```

先核对 `rev-parse HEAD` 与选定完整 SHA 相同；helper 的本地来源清单由该 checkout 提供。私有 raw HTTPS 的认证消费尚未验证，当前不用远程 raw URL 代替此步骤。采用个人工作流时显式增加 `--adopt-workflow` 并保留备份；否则保留已有未管理工作流并生成候选。后续 helper 更新使用新固定提交的 `install`，比较基线/本地/目标，保留用户编辑与 `.new.<hash>` 冲突候选，再按安装 revision 回滚；不整目录覆盖。

私有源库同步不创建正式 tag/release，也不代表 `license_decision=pending` 或本地候选政策已解除。未来公开由用户自行决定，公开前另选本库许可证、审查第三方来源并完成发行与远程消费验收。

## 技术栈规范查询与获取

初始化安装包含来源解析。已有项目按包读取依赖/锁定版本与配置命令；空白项目声明讨论确定的目标。先查询个人来源及随库规范，不匹配时获取固定提交/摘要的官方资料，生成项目范围的规范草案和中文来源报告。缓存可离线复用。

```sh
# 安装前查询；获取缓存不等于项目适配完成。
python3 scripts/personal.py query-stacks --project /path/to/project
# 已确认的空白项目。
python3 scripts/personal.py install --project /path/to/project --stacks python sqlite --stack-versions python=3.12.0
# 私有源库已克隆并核对完整提交；用同版本地清单。
python3 /path/to/personal-trellis/scripts/personal.py install --project /path/to/project --stack-registry /path/to/personal-trellis/stack-sources.json
# 只用随库规则与摘要核对通过的缓存。
python3 .trellis/personal/personal.py query-stacks --project . --offline
```

`--stack-registry` 使用同一固定提交 checkout 中的本地 `stack-sources.json` 消费当前私有库。这是个人 helper 的 profile 清单，原生 marketplace 仍使用 `index.json`。[可执行合同](specs/process/stack-sourcing.md)定义格式与错误行为。`build` 根据 catalog 生成个人 profile 的路径/摘要，并组合 `official-sources.lock.json` 中的官方参考，产出根目录 `stack-sources.json`；私有远程 raw HTTPS 获取与原生 SSH 拉取分开验收。

当前有 **53 个技术栈入口、52 份随库栈规则**（含 Vue 2/Boot 2 两份专项），覆盖语言/运行时、Web/后端框架、移动/桌面/微信、存储/ORM 和构建工具。[完整中文分组清单](STACKS.zh-CN.md)说明每项机制、版本边界、识别证据和缺口；`python3 scripts/personal.py list-stacks` 输出整个规范库的分组 JSON，`--format markdown` 显示中文表格。React、Go、Rust保持固定提交/摘要的官方获取 fallback，三个验收样例不代表全部覆盖。

新增大部分规则是 COMMON 共性工程基线，不承诺发布版本 API 或全部栈真实业务运行。`stack-definitions.json` 是可校验的精确依赖/清单 marker 与能力/provider 数据；改规则/catalog/定义/官方 profile 后运行 build/validate。build 生成 stack-sources.json、覆盖总览和带源哈希的默认 bundle；原生 index.json 保持独立。新增未列入的栈仍可声明并走官方来源补充。

项目产物为五类短索引、按包的 `stacks/<stack>/project-<scope-hash>.md`、`.trellis/personal/spec-sources.json` 和中文 `spec-sources.zh-CN.md`。源码缓存留忽略目录。AI 仍需核对实际模块、错误/类型和验证命令并记录本地调整；不得把草案或命令发现写成已完成适配/测试。

Vue 2/Boot 2 选择独立 major-2 规则，不安装 Vue 3/Boot 3–4 基线；未知版本不在两套规则中猜选。Java 1.8/VERSION_1_8 保留原值并归一化为 8；Gradle Kotlin DSL 不当 Kotlin 应用；C# LangVersion/.NET TFM/SDK、Dart/Flutter、Swift tools/编译器/SwiftUI SDK 分开。数据库精确依赖只识别引擎，驱动版本不作为服务端版本。未知栈/版本、无现成规范、离线未缓存或不匹配都保留缺口和定向检索问题。CLI `2` 表示有缺口/冲突，可用资产仍保留；`0` 只代表本步骤通过。已有规范优先，本地编辑生成候选，回滚只恢复本次受管理写入。

## 主代理与执行子代理

默认沿用 Trellis 的代理调度：主代理负责讨论、设计、派发、进度、整合和最终验收；`trellis-implement` 实施，随后由独立的 `trellis-check` 检查并修复。探索探子继续只读。当前任务的 implement.jsonl/check.jsonl 必须先列好适用规范，派发明确活动任务、文件归属和验证范围。子代理执行期间，主会话可回应用户并处理独立疑问；共享契约变化需协调后再继续。

Codex 的配置为 `.trellis/config.yaml` 中的 `codex.dispatch_mode: auto`。已有项目若明确选择 `inline` 或 AGENTS.md 限制子代理只读，接入时先核对并按用户意图协调；本包不会静默覆盖这些配置。活动轮次仍受已加载的执行模式约束，配置修改与真实子代理派发分开验证；不能把配置有效写成子代理已运行。

## 工具与设计交付
基线为 CodeGraph、RTK、QMD，按场景使用；版本和运行证据见 `tools.lock.json`。项目使用数据库时启用一个兼容 MCP，已支持的 SQL 引擎候选为 DBHub，Toolbox 可替代；Redis/MongoDB 不默认选择 DBHub，记录兼容 provider 待选择。凭证引用、模型/索引/二进制、业务设计留消费项目。

探索先满足用户明确指定的来源/提供者及限制，再复用已有能力和有效证据，只为缺口补一个最小提供者。默认不同时加载四来源、聚合器全部通道或重复搜索后端；linux.do、X、指定 Google 按需加载。未请求来源为 `selection_state=not_requested`，已选缺凭证为 `pending`；完成范围按本轮已选能力计算，显式要求四类时全纳入，替代入口不能冒充指定来源/工具通过。[唯一路由规范](specs/tools/exploration/usage.md)维护可调整预算（1–3 问题、每问题最多 3 去重候选、深读 1–2）、定向原文、扩展与停止条件；[中文报告模板](templates/reports/exploration.zh-CN.md)记录选择/复用、实际调用与覆盖。资产安装不安装外部研究服务器；配置存在不代表客户端加载，实际工具数量未知就记 unknown，不宣称规则已实现懒加载或固定 token 节省。

用户 PRD 讲背景、业务全景、模块与逐功能流程；TDD 保留十二章并按类型选择实现契约与图；新 UI 先确定语言/框架/交互，再开发。设计源、token/组件、模块画廊、真实功能原型、供用户手动导入的 Figma/MasterGo 文件、独立预览骨架与目标栈参考使用同版 ID/验收映射。实际工具、跨栈消费和本地预览运行须有独立证据；平台导入由用户操作并反馈，当前库版本不能单凭静态验证宣称全项支持。

UI 设计场景见 [使用规范](specs/tools/ui-design.md) 与 [personal-design 的按需参考](skills/personal-design/references/ui-skills.md)：Impeccable 用于规划/评审/打磨，UI UX Pro Max 补设计资料查询。UI 项目初始化缺少时安装，兼容版本复用；纯后端项目不安装该配置。两工具的固定版本、实际查询/检测和重复安装已验证；客户端自动选中和自动 hook 单列，当前使用显式检测。

```sh
# 完整工具初始化：UI 栈或已安装的 ui 能力会自动选中设计工具；空白 UI 项目加 --ui。
python3 .trellis/personal/library/scripts/tools.py --project . --ui
# 只补齐设计工具。
python3 .trellis/personal/library/scripts/tools.py --project . --tools impeccable ui-ux-pro-max
```

已安装的技能在后续回合可被客户端发现；Codex 可用 `$impeccable`、`$ui-ux-pro-max`，以实际客户端发现状态为准。来源、版本、文件归属和备份保留在项目私有运行目录；本地修改生成候选，不覆盖旧文件或现有 hook。安装工具不绕过 UI 设计确认。[需求管理示例记录](examples/ui-module/docs/review.zh-CN.md)展示当前预览的实际使用结果。

检测不执行脚本/依赖/Docker，也不自动安装目标应用 runtime。npm/pnpm/yarn/bun 命令按 packageManager/锁文件与真实 scripts 生成，未声明 runner 时 npm 仅为待确认示例。动态 Gradle alias/继承、复杂 YAML、未解析的锁文件保留诊断；Python 3.9/3.10 无 tomli 时仅静态单行 TOML，完整结构请使用 Python 3.11+ 或已有 tomli。独立安装复制全部定义/覆盖表/helper；运行仍不依赖维护目录。
