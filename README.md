# 个人 Trellis 可选指南与资源

使用 Trellis 原生讨论、任务、实施、检查与收尾。当前为 **1.0.0 未正式发布候选**，私有仓库 `zyf3313/personal-trellis`，许可证待定。

原生 `index.json` 只有 `personal-core` 规范条目，直接指向 `spec/`，不提供工作流或个人 Skill。三个 [个人约定](spec/guides/personal-conventions.md)、[可选文档一致性](spec/guides/document-consistency.md)、[按需工具选型](spec/guides/tool-selection.md) 平铺在 `spec/guides/`。按任务需要将相关链接加入项目现有规范索引或 JSONL，保留项目自己的索引、规则和原生工作流；无需每个任务完成 PRD/TDD/UI。

固定已核验提交后可使用原生规范入口（`FIXED_COMMIT` 为占位，先在独立项目验证）：

```sh
trellis init --registry 'git@github.com:zyf3313/personal-trellis#FIXED_COMMIT' --template personal-core --append
```

复用已有 Git 认证，不在 URL/日志中放凭证。`--append` 只补缺失文件，不合并更新。无个人初始化安装器，不安装、连接或配置任何工具。七维候选与待定状态见 [工具选型](TOOL-SELECTION.zh-CN.md)。

11 份 `templates/` 中文模板、[UI 示例](examples/ui-module/README.md)及 [Vue/Storybook 预览](apps/design-preview/README.md) 可主动复制使用。示例的历史工具记录不代表当前工具选择；预览依赖不为业务项目选择技术栈，不自动安装依赖。保留原有 92 文件字节。

旧消费项目的可选一次性退役见 [交付说明](DISTRIBUTION.zh-CN.md)，默认预览并保护修改。源库不再保留旧工作流、分类 catalog/bundle、三个个人 wrapper 或工具安装器，也不将其藏到归档继续加载。

[变更](CHANGELOG.md) · [第三方说明](THIRD_PARTY_NOTICES.md) · [确定性打包](scripts/release.md)
