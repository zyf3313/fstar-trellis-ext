# v1.0.0 本地交付候选

本包为可复现的本地发布候选，`library.json` 保持 `1.0.0 / not_published`。`zyf3313/personal-trellis` 私有 GitHub 源库已建立并同步；固定提交的原生 SSH 规范/工作流获取已实测，范围见下节。个人库许可证尚未选择（`license_decision=pending`），未创建正式标签或 release；候选政策仍为 `local_candidate`，清单的 `externally_publishable=false` 保留公开发行门禁。第三方身份与许可记录见 [来源说明](THIRD_PARTY_NOTICES.md)，不把任何第三方许可推定为本库许可。

需要 Python 3.9+；已验证原生 CLI 基线为 Trellis 0.6.9。预览和工具的实际环境要求分别见锁文件和各自 README，资产安装不安装这些运行依赖。Python 3.9/3.10 TOML 解析限制沿用主 README，运行平台/客户端/模型状态需要目标环境另验收。

## 打包与核验

命令维护与错误合同见 [release.md](scripts/release.md)。

在完整源库或解包目录执行：

```sh
python3 scripts/personal.py validate
python3 scripts/release.py build --output /path/to/candidate-one
python3 scripts/release.py build --output /path/to/candidate-two
cmp /path/to/candidate-one/personal-trellis-1.0.0-local-candidate.zip /path/to/candidate-two/personal-trellis-1.0.0-local-candidate.zip
python3 scripts/release.py verify --archive /path/to/candidate-one/personal-trellis-1.0.0-local-candidate.zip
cd /path/to/candidate-one
shasum -a 256 -c personal-trellis-1.0.0-local-candidate.zip.sha256
```

`release-policy.json` 明确列出允许的根文件、资产目录和必需的六个原型源码。构建与核验共享策略检查；核验同时拒绝缺少声明根文件/必需源码、清单与 library 版本或发布状态不一致、未经审阅的许可策略。归档为按路径排序、固定 1980 时间/普通 0644 文件模式的 ZIP，采用 STORE，无压缩器版本差异。每个交付文件在 `release-manifest.json` 中记录相对路径、字节数和 SHA256；清单自身不自引用，整个 ZIP 的 SHA256 覆盖清单。外置 `.manifest.json` 与包内清单相同，`.zip.sha256` 校验整个归档。校验失败退出 1，成功退出 0。摘要验证完整性，需要可信来源提供摘要才能建立真实性。

保留原生 `index.json`、`bundles/personal-core`、规范/工作流/skills/模板/adapter/helper/tests，以及锁定预览和示例源码、设计源与生成交付资产。`examples/ui-module/runtime` 的六个原型源码是明确例外；其他 runtime 内容拒绝打包。排除 node_modules、dist、pycache、Git、缓存、私有目录、运行配置、备份、证据和 env 文件。允许范围内的软链接、非普通文件、候选 `.new.*`、私钥/数据库/日志/状态文件及不安全路径会失败。未知根资产不进入候选；需要扩展时审阅 allowlist。打包输出须置于允许源目录以外。

## 本地安装、更新、冲突与回滚

以下流程在隔离消费目标执行。先核验归档，再解包，固定使用解包后的 library；本地路径仅用于 helper，不能传给原生 registry：

```sh
python3 -m zipfile -e /path/to/personal-trellis-1.0.0-local-candidate.zip /path/to/unpacked
cd /path/to/project
trellis init --codex -u YOUR_NAME -y --skip-existing
python3 /path/to/unpacked/personal-trellis-1.0.0/scripts/personal.py install --project . --stacks python sqlite --stack-versions python=3.12.0 --offline --adopt-workflow
python3 .trellis/personal/personal.py detect --project .
python3 .trellis/personal/library/scripts/personal.py validate
```

固定栈示例用于隔离消费，不替代实际项目选型。`--adopt-workflow` 是明确采用并备份个人工作流；省略时保存已有未管理工作流并生成候选。新项目/已有项目均由 `.trellis/personal/install.json` 记录版本、revision 和文件基线。运行 helper 不依赖维护者源码位置；解包源和目标的运行配置/备份/证据分开。

本地更新实际入口仍为目标版本的 `install`，无独立 `upgrade` 参数：

```sh
python3 /path/to/NEXT_FIXED_CANDIDATE/scripts/personal.py install --project /path/to/project --offline
python3 /path/to/NEXT_FIXED_CANDIDATE/scripts/personal.py rollback --project /path/to/project --revision REVISION_FROM_INSTALL_JSON
```

与已安装基线相同的本地文件可更新；用户编辑保留，目标内容形成 `.new.<hash>` 冲突候选。相同版本重复安装复用不变资产；退出 2 表示来源缺口或冲突，需查看中文来源报告与 actions。手动比较/确认候选后再继续，不能把退出 2 当所有安装失败或全部通过。回滚只恢复该 revision 的受管理写入；后续本地编辑会成为冲突并保留。备份位于目标 `.trellis/personal/backups`，不能纳入分发包。本地相同版本更新与冲突/回滚可验证；不同远程版本升级尚未通过。

## 私有源库与原生远程消费

2026-10-13 在 macOS / Trellis 0.6.9 实测的完整提交为 `54d43df5356f493fdaff2f88459b5e83b19a1aaf`。独立 SSH 克隆的 252 文件摘要与冻结源一致，原生 init 的 25 份 spec 逐字节匹配，workflow 候选与固定提交一致，当前修改保留；同提交 append 保留修改并补回缺失文件。复制后的 helper 在原 checkout 不可用时 detect/validate 通过，修改保护与 revision 回滚通过。31 项检查通过；其他版本/ref 升级、公开 HTTP、用户/平台/设备/Linux/模型及第二次远程 workflow 调用分别保留未验收状态。这一提交是已验证运行基线；说明的后续提交不自动扩展该范围。

首次原生 bundle + helper 组合安装会生成三份索引候选，并退出 `2`：`.trellis/spec/guides/personal/index.md`、`engineering/index.md` 和 `tools/index.md`（后两者位于同一 personal 目录）。原生 bundle 索引保留，按项目实际栈生成的新索引写为 `.new.<hash>`。查看 install 的 `actions` 和具体 candidate，比较并合并项目需要的链接，保留用户已有调整，再重新运行 install 和项目规范检查。资产与复制 helper 已可用，不把未处理候选称为初始化全部完成，也不整目录强制覆盖。唯一定义见 [registry adapter](adapters/registry/README.md)。

完整库作为 `zyf3313/personal-trellis` 的仓库根，保持 private，排除任务、会话、证据、维护项目业务和依赖目录。消费前复用已有 GitHub SSH 身份并确认私有仓库读取权限；不写入 token，不修改全局 Git/SSH 或客户端配置。Trellis 0.6.9 的 GitHub HTTP registry index 不携带认证，`gh:`/`GIGET_AUTH` 不能单独解决私有库的 index 读取；SSH source 强制走 Git backend。

以下 `FIXED_COMMIT` 必须替换为已推送并核验的完整提交 SHA。实际值记录在独立消费证据中，文档保留占位，避免为包含本文的提交写入自引用 SHA：

```sh
trellis init --registry 'git@github.com:zyf3313/personal-trellis#FIXED_COMMIT' --template personal-core --append
trellis workflow --template chinese-design-first --marketplace 'git@github.com:zyf3313/personal-trellis#FIXED_COMMIT' --create-new
```

`--append` 仅补缺失 spec，不承担升级合并；`--create-new` 总是写入 `.trellis/workflow.md.new`，保留当前工作流与其 hash 记录，无论当前工作流是否修改。先比较候选后采用；省略此参数时，未修改的工作流可以直接安装，本地修改则需显式处理。认证与门禁的七节可执行合同见 [registry adapter](adapters/registry/README.md)。Trellis 0.6.9 resolver 不接受本地目录、file:// 或普通 localhost 静态 registry；helper 本地安装、解析器/帮助验证均不算原生远程拉取成功。固定提交的 spec/workflow 拉取、重复消费与修改保护要在真实 Git remote 分别验收。

spec/workflow 下载不会隐式安装本包配套 helper、技能、模板、工具或 hook。私有 raw HTTPS 的认证获取尚未验证，配套资源和技术栈清单当前从同一已核验提交的本地克隆获取：

```sh
git clone --no-checkout git@github.com:zyf3313/personal-trellis.git /path/to/personal-trellis
git -C /path/to/personal-trellis checkout --detach FIXED_COMMIT
git -C /path/to/personal-trellis rev-parse HEAD
python3 /path/to/personal-trellis/scripts/personal.py validate
python3 /path/to/personal-trellis/scripts/personal.py install --project /path/to/project --stack-registry /path/to/personal-trellis/stack-sources.json
```

核对 HEAD 与选定 SHA 一致后运行 helper。显式 `--adopt-workflow` 才选择个人工作流并备份原文，否则保留已有未管理工作流并生成候选。helper 升级使用新固定提交的 `install`，沿用上节基线/本地/目标比较、`.new.<hash>` 冲突与 revision 回滚；原生追加、工作流候选和 helper 升级是三个独立验收，不能通过整目录覆盖代替。

本轮私有源码同步不创建正式 tag/release，安装包版本仍为 1.0.0，任务方案版本不作为发行版本。用户未来可自行决定公开；公开前需要另选本库许可证、审查第三方来源与许可、调整经过审阅的发行政策并完成公开发行验收。当前许可与 `not_published` 状态不因私有推送自动改变。

## 证据范围

本候选的自动化验收包括确定性归档、排除/完整性/恶意路径、干净解包校验、独立 helper 安装与复制调用，以及受管理文件的修改保护/回滚。自动化计数由本次运行记录提供，不能用历史结果替代变更后的最终检查。源码规则和模板存在不等于项目语义适配；测试用设计确认 fixture 不等于用户接受；Figma/MasterGo 手动导入、真实平台/客户端/模型、Linux 运行以及原生远程分发仍按实际环境记录。

`verify-design` 是设计摘要/映射的机械检查：非空确认引用和版本、文件摘要、产物关联可被核对；它不核实引用是否是真实用户确认，也不理解正文版本、评审状态或验收章节语义。开发前主代理仍须核对真实用户确认与正文状态，结果中的 `semantic_and_user_acceptance=requires_review` 保留此责任，不能把 helper 通过称为自动审核或完整开发拦截器。

## 通用行为来源与消费追溯

G 编号沿用原始提炼清单，规则 ID/路径/target 从当前 catalog 的 `origin_ids` 映射核对。来源是提炼依据的类别与锚点，消费路径是交付后目标项目的落位；本说明不链接维护项目的私有任务或本机路径。

| 编号 | 提炼来源锚点 | 当前规则源 / catalog ID | 消费目标 | 验收边界 |
|---|---|---|---|---|
| G01 | 项目效率约束：Start and resume；工作区与归属 | [core.context](specs/core/context.md) | `.trellis/spec/guides/personal/core/context.md` | 来源/落位可静态核对；具体项目行为与语义待验收 |
| G02 | Trellis Phase 1 / brainstorm；用户设计优先要求 | [process.planning](specs/process/planning.md) | `.trellis/spec/guides/personal/process/planning.md` | 来源/落位可静态核对；具体项目行为与语义待验收 |
| G03 | 前端 quality-guidelines：90、170；用户 UI 基线要求 | [process.ui-design](specs/process/ui-design.md) | `.trellis/spec/guides/personal/process/ui-design.md` | UI 项目条件适用；真实交互/设备与用户接受另验收 |
| G04 | capability discovery/ownership；guides:20；文档权威 | [process.document-ownership](specs/process/document-ownership.md) | `.trellis/spec/guides/personal/process/document-ownership.md` | 来源/落位可静态核对；具体项目行为与语义待验收 |
| G05 | before-dev / spec-bootstrap；用户来源与适配要求 | [process.bootstrap](specs/process/bootstrap.md) | `.trellis/spec/guides/personal/process/bootstrap.md` | 来源/落位可静态核对；具体项目行为与语义待验收 |
| G06 | 效率约束:7、9；CodeGraph 与基础文档规则 | [core.context](specs/core/context.md) | `.trellis/spec/guides/personal/core/context.md` | 来源/落位可静态核对；具体项目行为与语义待验收 |
| G07 | Trellis Phase 2；用户默认执行代理澄清 | [core.collaboration](specs/core/collaboration.md) | `.trellis/spec/guides/personal/core/collaboration.md` | 本项目已执行派发；其他客户端真实路由另验收 |
| G08 | guides:18；database:16；java-coding:94；唯一职责 | [engineering.common.architecture](specs/engineering/common/architecture.md) | `.trellis/spec/guides/personal/engineering/common/architecture.md` | 来源/落位可静态核对；具体项目行为与语义待验收 |
| G09 | guides:11、30；frontend testing:24；跨层消费者 | [engineering.common.architecture](specs/engineering/common/architecture.md) | `.trellis/spec/guides/personal/engineering/common/architecture.md` | 来源/落位可静态核对；具体项目行为与语义待验收 |
| G10 | guides:14；data-access-control:88、102；信任边界 | [engineering.common.contracts](specs/engineering/common/contracts.md) | `.trellis/spec/guides/personal/engineering/common/contracts.md` | 仅存在该信任边界时适用；真实身份/资源验证另验收 |
| G11 | frontend quality:92、100、173；testing:30、42 | [engineering.frontend.interaction](specs/engineering/frontend/interaction.md) | `.trellis/spec/guides/personal/engineering/frontend/interaction.md` | UI 项目条件适用；真实交互/设备与用户接受另验收 |
| G12 | backend error-handling:81；audit:46；错误/日志 | [engineering.common.errors](specs/engineering/common/errors.md) | `.trellis/spec/guides/personal/engineering/common/errors.md` | 来源/落位可静态核对；具体项目行为与语义待验收 |
| G13 | 效率约束:26；capability verification evidence | [core.verification](specs/core/verification.md) | `.trellis/spec/guides/personal/core/verification.md` | 来源/落位可静态核对；具体项目行为与语义待验收 |
| G14 | 效率约束:32；guides:43；证据复用 | [core.verification](specs/core/verification.md) | `.trellis/spec/guides/personal/core/verification.md` | 来源/落位可静态核对；具体项目行为与语义待验收 |
| G15 | project-usage:15、97；用户安装/回滚要求 | [process.bootstrap](specs/process/bootstrap.md) | `.trellis/spec/guides/personal/process/bootstrap.md` | 本地资产保护/回滚自动化；工具/client 与远程另验收 |
| G16 | 用户变更同步要求；Trellis Phase 2 rollback / Phase 3 spec update；guides:47 | [process.change-control](specs/process/change-control.md) | `.trellis/spec/guides/personal/process/change-control.md` | 自动门禁 fixture 与真实用户冻结/变更接受分开 |
