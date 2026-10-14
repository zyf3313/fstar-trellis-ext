# 确定性本地候选合同

## 范围

只分发 release-policy.json 明确列出的 guides、可选模板/UI资源、退役脚本、测试及说明。版本 1.0.0、私有、未正式发布、许可证待定。无工作流、个人 wrapper、分类生成或默认工具安装。

## 输入

Python 3.9+，完整源目录。UI npm 锁文件与源保持既有字节；无改动时不重复构建。

## 构建

```sh
python3 scripts/release.py build --output /tmp/candidate-one
python3 scripts/release.py build --output /tmp/candidate-two
```

## 完整性

```sh
python3 scripts/release.py verify --archive /tmp/candidate-one/personal-trellis-1.0.0-local-candidate.zip
python3 -m unittest discover -s tests -v
```

两份 ZIP 须同 SHA256；manifest 包含每个源文件字节数及摘要。解包后独立复核。

## 排除与失败

排除依赖、缓存、运行目录、凭证、候选文件和日志；拒绝软链接、不安全路径、缺少必需文件、摘要或元数据不一致。完整性不证明真实用户/设备接受。

## 退役与恢复

退役入口见 [分发说明](../DISTRIBUTION.zh-CN.md)。只按旧管理摘要处理，默认预览、before-image、恢复后修改保护；不安装或卸载任何工具。

## 证据

记录代码状态、环境、命令、退出码、耗时及真实 pass/fail/skip。私有同步、远程原生消费与公开发行分别验收；当前不授予公开许可。
