# DBHub 接入

只有使用数据库的项目启用。复制 `source-manifest.example.json` 到具体项目，填写引擎、明确环境、来源 ID 和本地 DSN 环境变量名。清单不包含连接密钥；默认使用只读来源。需要开发/测试写能力时添加独立来源并设置 `readonly: false`。

```sh
python3 .trellis/personal/library/scripts/database.py --project . --manifest db-sources.json --connect
```

缺凭证会记录 `missing_credentials`，没有来源记录 `not_applicable`。配置冲突生成候选并保留现有配置。`--connect` 实际连接并执行有限读取探针；初始化不自动向业务库写测试数据。所需写入验收使用可丢弃环境和 `tests/database_acceptance.py`，正式操作依据数据库场景规范及项目迁移。

参数化自定义工具和单次事务的行为以锁定的 DBHub 1.5.0 为准。SQL 返回中的 `statements[].count` 才是该版本的影响/返回数量字段；`max_rows` 只限制查询结果。跨调用会话、超时回滚和账号权限不得由提示推断。客户端加载、连接读取与所需写验收分别记录。
