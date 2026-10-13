# 两功能设计与交互交付示例

<!-- personal-ui-module-generated -->

> 本说明从源库 README 生成，不独立编辑。本目录是可单独复制的静态导出；以下依赖安装、构建和校验命令须在完整源库的 `examples/ui-module/` 中执行。

这是用于评审规范库能力的需求工作台，风格为待用户评审示例。包含浏览与新建两功能、八张页面/状态图，以及真正可输入、校验、失败恢复和导航的本地原型。数据为模拟，尚未接入业务后台或正式权限系统。

```sh
npm ci --registry https://registry.npmjs.org
node build.mjs
node verify.mjs
python3 -m http.server 8874 --bind 127.0.0.1 --directory generated
```

打开 `/gallery.html` 按模块→功能→状态查看设计，`/prototype.html` 可操作。运行只提供 `generated/` 目录。PRD/TDD 在 [docs](docs/prd.zh-CN.md)；唯一设计源为 [design.json](design.json)，原型参考实现是 `runtime/` 的 HTML/CSS/JavaScript。具体项目按已确认技术栈映射自己的组件库。

`generated/exports/requirements.sketch` 是公开 ZIP/JSON 格式 146，含真实可编辑矩形与文本，不是图片打包或改名的 JSON。构建固定依赖、ID、ZIP 时间和源/脚本/模板摘要；修改 source 或 runtime 后重新生成。`manifest.json` 记录生成输入及产物摘要，`verify.mjs` 检查 schema、回读、复现及源漂移。

Figma 使用官方 “Import Sketch files” 入口；MasterGo 在工作空间导入 Sketch 文件。一次选文件可导入全部八画板。用户手动导入后可核对：画板数量、中文文字可编辑、矩形层、颜色/字体/尺寸和差异。字体须在平台可用；文件不包含原型连线、平台变量/Auto Layout 或共享组件实例，浏览器原型单独提供。MasterGo 官方说明不会保留 Sketch 原型连线，不把该交换文件宣称为通用无损原型格式。

平台编辑不会自动回写 JSON。影响设计的修改需同步权威 source、递增版本，再生成并更新证据。当前 manifest 记录 `manual_import_file_ready` 和尚未收到的用户平台反馈，文件检查通过不宣称平台导入无损。独立可扩展预览工程位于 `../../apps/design-preview`。
