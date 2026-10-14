# 个人 Trellis 规范库

这个私有库提供按场景启用的跨项目规范和配套中文模板。它不替代 Trellis 原生 workflow、任务生命周期、代理调度、目标项目规范索引或本地规则，也不安装、连接或配置任何工具。当前版本为 **1.0.0 未公开发布候选**，许可证决定仍为 pending。

`index.json` 只注册一个 `personal-core` spec 模板，路径为 `spec/`。固定并核验提交后，在隔离项目或目标项目执行：

```sh
trellis init --registry 'git@github.com:zyf3313/personal-trellis#<fixed-commit>' --template personal-core --append
```

复用已有 Git 认证，不在 URL 或日志中写凭证。`--append` 只把该固定提交中的 `spec/` 内容加入项目；执行前后核对目标项目已有 workflow、配置、hooks、索引和本地规范。若目标路径已有本地修改，先比较和备份，不能用个人库版本直接覆盖。该命令不会证明任何可选工具已经安装、加载或实测。

## 单链接启用

导入后，按项目意愿在现有规范索引或任务 JSONL 中引用一次 [`spec/personal-index.md`](spec/personal-index.md)。该页负责场景路由；项目继续拥有自己的索引，不由本库分发 `guides/index.md`。任务只读取命中的指南和必要模板，小修复不强制生成 PRD、TDD 或 UI 设计。

`spec/templates/` 随同原生 registry 一起导入。生成中文 PRD/TDD、UI 基线、功能交互、变更记录或参考项目探索时，从本地已导入的模板中只读取所需文件，不再从仓库根目录定向下载模板。

## 更新边界

Trellis runtime 升级与个人规范固定提交更新是两件独立的操作：

1. 升级 Trellis runtime 时遵循目标项目的原生升级流程，核对 workflow、配置、hooks 与项目索引；不要用个人库替代运行时文件。
2. 更新个人规范时先审阅旧固定提交到新固定提交的差异，在隔离项目执行原生 append/兼容检查，再把目标项目记录的个人 ref 更新到已核验提交。
3. 两种更新都先识别本地修改和所有权，保留备份或可恢复提交；发现冲突时比较后合并，不声称 `--append` 会自动更新或合并已有文件。
4. 分别记录源 ref、目标 Trellis 版本、实际新增/修改文件、保护结果和场景检查。只有代码状态、环境、命令和范围都未变化时才复用旧证据。

本库不含个人 workflow、安装器、meta-Skill、catalog/bundle 层级、UI 演示应用、Storybook 预览或自制发布脚本。需要真实工具连接、设计平台导入、数据库访问、浏览器/设备验收时，由具体项目在明确授权和环境中完成并记录。

[场景入口](spec/personal-index.md) · [变更记录](CHANGELOG.md)
