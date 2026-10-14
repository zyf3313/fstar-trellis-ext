# 工具选型台账

以下为已选定的**用途与路由**，不表示每个项目默认必装，也不表示当前客户端已安装、已加载或已实测。既有安装和 UI 示例的历史记录不作本批运行证据；原生 Trellis 流程保持。

| 维度 | 当前选择与触发 | 未选部分 / 替代 |
|---|---|---|
| 探索 | [Web 调研](spec/guides/web-research.md)：已有 Web；GitHub 优先复用 gh，Exa 补充召回；linux.do 按相关性或用户指定 | Google / X 等按需；内网仅复用项目已授权入口 |
| 代码理解 | [CodeGraph](spec/guides/code-search.md) 查结构；字面量 rg；已知小文件直读 | 缺图或异常用定向源码，遵循项目索引修复约定 |
| 项目知识检索 | [QMD](spec/guides/knowledge-search.md) 跨文档关键词优先，语义按需 | 已知文件直接读；原生索引与文本检索兜底 |
| 需求/方案表达 | 原生 Trellis 讨论/任务与按需中文模板 | 图示等随具体项目选，不加固定产物门禁 |
| UI 设计原型 | [emil-design-eng](spec/guides/ui-design.md) 唯一核心；break-ui / review-animations / mobile-native 按数据、动效、手机条件 | 已有项目设计基线优先；设计平台/本地预览按需 |
| 运行调试验收 | 复用项目现有命令、日志和适用的浏览器/设备检查 | 其他调试工具按需；无设备时真机验收 pending |
| 数据库 | [DBHub](spec/guides/database-access.md) 可选入口：显式只读与行上限，写入口独立授权范围 | 已授权项目入口、schema/fixtures 兜底 |

当前批次只交付规范。每个消费项目分别记录工具版本/来源、安装或可发现状态、客户端实际加载、任务实测结果及缺口；未提供这些证据前均为未核验，不能因 registry 拉取成功改成“已接入”。效果、中文召回、资源和成本以目标环境验证，不锁另一机器的 PATH、模型、价格或额度。

UI 个人方案移除 frontend-design 并列主导路线；Impeccable / UI UX Pro Max 不作为当前默认备选或并行主设计者。机器已有 Skill 不卸载。三个 Emil 专项不是固定三关；经验阈值服从项目基线，性能以实测判断。

选型不触发安装、连接、建索引、embed、账号/模型调整；真正接入另在明确范围内实施。工具缺失先复用现有替代或说明缺口。无默认安装器、新流程或额外 Skill 包装。
