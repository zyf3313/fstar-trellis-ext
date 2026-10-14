# 个人 Trellis 规范库

这个私有库提供按场景启用的跨项目规范、配套中文模板，以及一个可选的个人初始化包装命令。它不替代 Trellis 原生 workflow、任务生命周期、代理调度、目标项目规范索引或本地规则。当前版本为 **1.1.0 未公开发布候选**，许可证决定仍为 pending。

## 一次初始化

从已经核验并 checkout 的个人仓库运行：

```sh
./bin/trellis-personal init --project /path/to/project -- --codex --user FrancisZhang
```

包装器先调用已安装的原生 `trellis init`，固定当前个人仓库 HEAD 作为 registry ref，并以 `personal-core` 和 `--append` 导入本库 `spec/`。原生参数只能放在 `--` 后；`--registry`/`-r`、`--template`/`-t`、`--append` 和互斥的 `--overwrite` 由包装器拥有，不能覆盖。若不是从 origin 为 `zyf3313/personal-trellis` 的 checkout 运行，必须显式传完整提交：

```sh
./bin/trellis-personal init \
  --project /path/to/project \
  --personal-ref '<40-character-commit-sha>' \
  -- --codex --user FrancisZhang
```

先用 `--dry-run` 查看计划；它不执行外部变更，也不写报告。`--skip-tools` 只执行原生初始化并把工具准备记为 deferred。`--agent` 选择 Emil Skills 的安装与检测目标，默认使用 Codex 用户范围，也可选 `claude-code`；若设置了 `CODEX_HOME` 或 `CLAUDE_CONFIG_DIR`，使用对应配置目录下的 `skills/`，否则使用 `~/.codex/skills` 或 `~/.claude/skills`。包装器要求 Python 3.9+，所有外部命令都以参数数组执行。

原生初始化成功后，包装器检测并只准备缺失项：

- 用 npm 固定安装 CodeGraph `1.6.2` 与 QMD `2.5.3`；
- macOS 且已有 Homebrew 时安装缺失的 GitHub CLI；Linux 不自动提权，报告官方手工安装动作；
- 检测 Emil 的核心 Skill 与三个条件专项 Skill；若有缺失且 `npx` 可用，以一次固定的 `skills@1.7.0` 调用只安装缺失项，并在所选 Agent 的真实目录中逐项复核 `SKILL.md`；
- 仅在可识别的代码项目缺少 `.codegraph/` 时执行 `codegraph init`。

Emil 安装命令固定为 `npx -y skills@1.7.0 add emilkowalski/skills`，每个缺失项追加一次 `--skill <name>`，最后追加 `-g -a <codex|claude-code> --yes`。`npx` 不可用时记为 `unsupported`；命令退出非零或安装后仍有缺失时整体记为 partial。已实际出现在目标目录的 Skill 仍准确记为 `installed`，不会因同批其他项失败而抹去结果。包装器准备和客户端加载是两个状态，首次真正进入 UI 场景时仍要确认客户端已经发现对应 Skill。

QMD collection/embed/模型下载、`gh auth login`、DBHub 数据源/凭证/写权限和 Exa API key 永远留到对应场景首次使用。包装器不收集这些秘密，也不自动连接账号或数据库。结果写入目标项目 `.trellis/personal/bootstrap-report.json`，区分 `installed`、`already_available`、`deferred`、`unsupported` 与 `failed`；工具失败保留已经成功的原生初始化并以 partial 非零退出。原生 CLI 的零退出码还必须同时没有显式 `Error:`、真实生成 `.trellis/spec/personal-index.md`，并在 `.trellis/config.yaml` 记录本次固定 registry source 与 `personal-core` template，否则按失败短路。报告路径的既有符号链接或非目录父路径会在运行原生初始化前被拒绝，防止个人报告写出目标项目。

## 只导入规范

可以继续只运行原生 Trellis。`index.json` 只注册一个 `personal-core` spec 模板，路径为 `spec/`：

```sh
trellis init --registry 'git@github.com:zyf3313/personal-trellis#<fixed-commit>' --template personal-core --append
```

复用已有 Git 认证，不在 URL 或日志中写凭证。`--append` 把该固定提交中的 `spec/` 内容加入项目，原生 Trellis 还会在 `.trellis/config.yaml` 中记录该 registry source/template；它不应删除原配置内容，但配置文件不会保持逐字节不变。执行前后核对目标项目已有 workflow、配置、hooks、索引和本地规范。若目标路径已有本地修改，先比较和备份，不能用个人库版本直接覆盖。该命令只导入规范，不准备工具；工具是否可用仍需实际检测。

## 单链接启用

导入后，按项目意愿在现有规范索引或任务 JSONL 中引用一次 [`spec/personal-index.md`](spec/personal-index.md)。该页负责场景路由；项目继续拥有自己的索引，不由本库分发 `guides/index.md`。任务只读取命中的指南和必要模板，小修复不强制生成 PRD、TDD 或 UI 设计。

`spec/templates/` 随同原生 registry 一起导入。生成中文 PRD/TDD、UI 基线、功能交互、变更记录或参考项目探索时，从本地已导入的模板中只读取所需文件，不再从仓库根目录定向下载模板。

工具选择、安装/发现、客户端加载、任务执行和成功验收是不同状态。可选包装器只负责上述有界准备，包括缺失 Emil Skills 的固定版本安装；场景指南仍决定何时实际使用 CodeGraph、QMD、GitHub/gh、可选 DBHub 和 Emil。初始化报告不证明客户端已加载，也不证明任务执行成功。

## 更新边界

Trellis runtime 升级与个人规范固定提交更新是两件独立的操作：

1. 升级 Trellis runtime 时遵循目标项目的原生升级流程，核对 workflow、配置、hooks 与项目索引；不要用个人库替代运行时文件。
2. 更新个人规范时先审阅旧固定提交到新固定提交的差异，在隔离项目执行原生 append/兼容检查，再把目标项目记录的个人 ref 更新到已核验提交。
3. 两种更新都先识别本地修改和所有权，保留备份或可恢复提交；发现冲突时比较后合并，不声称 `--append` 会自动更新或合并已有文件。
4. 分别记录源 ref、目标 Trellis 版本、实际新增/修改文件、保护结果和场景检查。只有代码状态、环境、命令和范围都未变化时才复用旧证据。

本库不含个人 workflow、meta-Skill、catalog/bundle 层级、UI 演示应用、Storybook 预览或自制发布脚本。`bin/trellis-personal` 只是原生初始化调用方和有界工具准备器，不修改或 fork Trellis。需要真实账号连接、设计平台导入、数据库访问、模型下载、浏览器/设备验收时，由具体项目在明确授权和环境中完成并记录。

[场景入口](spec/personal-index.md) · [变更记录](CHANGELOG.md)
