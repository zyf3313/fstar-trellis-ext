# 变更记录

## 2026-10-14 · 1.1.0 未公开发布候选

新增可选的 `trellis-personal init`：先驱动原生 `trellis init`，再从固定个人提交 append `personal-core`，最后检测并准备缺失的 CodeGraph、QMD、受支持平台的 GitHub CLI 与 Emil Skills。Emil 使用一次固定的 `npx -y skills@1.7.0 add emilkowalski/skills` 调用，通过重复 `--skill` 只安装缺失项，以 `-g -a <agent> --yes` 选择 Codex 或 Claude Code，并在实际 Agent 目录逐项复核结果。命令非零时保留已验证成功的 Skill，同时整体形成 partial 报告；缺少 `npx` 才记为 unsupported。

兼容 Trellis CLI 自行补 `.git` 的 registry 输入；除退出码外验证显式错误、个人索引实际生成，以及配置中固定 registry source/template 的持久化，避免旧索引或原生 CLI 错误仍返回零时误报成功。代码项目缺少索引时才执行 `codegraph init`；原生初始化失败会短路，后续工具失败会保留成功初始化并形成 partial 报告。初始化安装、客户端加载和 UI 场景触发继续分别记录。

QMD collection/embed/模型、GitHub 登录、DBHub 真实连接/凭证/写权限和 Exa API key 保持 deferred。新增 dry-run、skip-tools、目标 Agent、固定 ref、原生参数透传、长短冲突参数拒绝、符号链接路径边界、脱敏报告和 fake PATH 隔离测试。原生 Trellis workflow/config/hooks 所有权不变。

## 2026-10-14 · 1.0.0 未公开发布候选

将个人库收敛为一个原生 `personal-core` spec：新增一页式 `personal-index.md`，保留七份按场景指南，并把七份中文模板迁入 `spec/templates/`，使原生 registry 一次取得指南与模板。中文 PRD/TDD、UI 设计、文档一致性和参考项目探索规则补齐为可独立执行的合同。

删除 UI 演示与 Storybook 工程、旧根模板层级、重复工具/分发说明、旧退役与打包脚本、布局测试及发布清单。固定提交的原生 append、目标项目单链接启用、Trellis runtime 与个人 ref 分开升级、本地修改保护和证据边界统一写入 README。

该版本没有初始化包装器；工具仍按场景可选，不默认安装或连接。Emil 保持唯一核心 UI Skill；专项能力仅按数据边界、动效或移动端条件使用。许可证 pending、私有、未公开发布状态不变。
