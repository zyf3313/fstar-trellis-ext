# 私有候选分发与旧版退役

版本保持 1.0.0 / not_published，私有，许可待定；不创建公开 release。当前原生 registry 仅 `personal-core` → `spec`，不包含 workflow。项目的 Trellis 原生流程、配置、hooks、索引和本地规范保持权威；按需在既有索引/JSONL 引用指南。不提供常驻个人初始化器。当前分发八个平铺指南，不创建 guides/index.md 覆盖消费者索引；五个场景按 README 导航按需使用。用途已选不等于工具已安装、已加载或已实测，接入/模型/连接另按明确任务处理。

## 旧消费项目的一次性退役

从本次已核验源运行，先对独立副本预览。真实 fstar 不执行本批迁移。

```sh
python3 scripts/retire-personal.py --project /path/to/old-project
python3 scripts/retire-personal.py --project /path/to/old-project --apply
```

只退役旧 `.trellis/personal/install.json` 明确拥有且摘要匹配的 `.trellis/spec/guides/personal/` 文件、三个 `.agents/skills/personal-project-init` / `personal-project-explore` / `personal-design` 文件，以及摘要匹配的 AGENTS 个人块。整个 AGENTS 文件的用户文本保留。编辑、新增、不明所有权、软链接保留并报告。其他命名空间的规范不做推断删除。

旧个人工作流默认保持；若其仍依赖个人规范/Skill，或 AGENTS 个人块无法安全移除，apply 在写入前整体阻止并退出 2，先处理原生活动入口再重试。已经原生且没有个人依赖的工作流不阻止退役。只有当前摘要匹配旧安装记录，且显式提供与项目 `.trellis/.version` 相同版本的原生候选才恢复：

```sh
python3 scripts/retire-personal.py --project /path/to/old-project --native-workflow /path/to/official-fixture/.trellis/workflow.md --native-version VERSION --apply
```

候选须来自该版本的独立官方 Trellis fixture；版本匹配和非空内容是机械边界，来源真实性由操作者审核。编辑过的旧工作流保留供人工比较。脚本不会改 `.template-hashes.json` 或替上游宣称受管理状态已更新；后续按原生 Trellis 更新流程审核。

apply 在任何修改前写 `.trellis/personal/retirement/UUID.json`，含 before-image、修改后摘要、原安装记录摘要和状态。中途失败亦可用此记录恢复。恢复默认预览，显式 apply 且当前摘要仍匹配退役后状态才恢复，拒绝覆盖后来编辑或重建的文件：

```sh
python3 scripts/retire-personal.py --project /path/to/old-project --restore UUID
python3 scripts/retire-personal.py --project /path/to/old-project --restore UUID --apply
```

旧 `.trellis/personal/` 运行目录、安装记录和备份保留，**不再作为活动初始化入口**；不要再运行旧 personal.py/tools.py。脚本不会卸载工具、改 MCP/provider skills/hooks/模型/索引/账号或业务文档。报告中的 preserved 表示需人工审阅，不代表已完成所有原生化；apply 或恢复中有 preserved 时返回 partial 和退出 2，完整完成才退出 0。重复执行仅处理仍匹配的资产。

## 候选验证

执行 [打包合同](scripts/release.md) 的 build/verify，两份归档须同字节；解包可独立运行测试。源清单、92 UI 文件摘要与本次验证证据分别保留。旧版数量/工具运行证据不能作为当前功能通过证明；真实远程消费、平台导入、浏览器/设备接受按实际新证据记录。
