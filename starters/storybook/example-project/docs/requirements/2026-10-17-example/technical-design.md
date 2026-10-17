# 示例项目：评审邀请技术方案
```meta
date: 2026-10-17
review_deadline: 2026-10-24
summary: 展示同一需求版本的技术实现、来源边界和生成流程。
```

> [!NOTE] 本文是 starter 样例，可按项目实际类型裁剪。

## 理解与范围 {#understanding}

Storybook 是可再生投影。Markdown、设计资产和原型源码仍由项目目录拥有。

## 总体方案 {#solution}

```flow
读取配置 | 解析 projectRoot 与 manifest
校验来源 | 阻止绝对路径和越界路径
生成投影 | 计算哈希并生成 stories
构建门户 | Storybook 输出静态站点
```

## 来源校验 {#source-validation}

生成器只读取项目根内的相对路径。必需来源缺失时退出失败；标记为可选的文档缺失时跳过对应入口。

## 字典定义 {#dict-review-status}

`REVIEW_STATUS` 是评审状态字典，当前取值为 `draft`（草稿）、`reviewing`（评审中）、`changes`（需修改）和 `approved`（已通过）。产品需求说明中的 `status` 字段引用本定义。

## 测试与影响 {#testing}

自动化覆盖缺失来源、正文修改、可选文档省略、生成确定性和最终 Storybook 索引。
