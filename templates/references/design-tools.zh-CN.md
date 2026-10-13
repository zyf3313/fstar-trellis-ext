# 设计文档与工具参考

PRD 先解释背景、业务全景、模块职责和逐功能行为；TDD 解释每个功能如何实现，按问题选流程、状态、时序、ER 或架构图。十二章骨架按项目真实类型裁剪，不强制 REST 或数据库。

开源结构参考：[WePay 设计模板](https://github.com/wepay/design_doc_template)、[Kubernetes KEP](https://github.com/kubernetes/enhancements/tree/master/keps/NNNN-kep-template)、[Go Proposal](https://github.com/golang/proposal)、[TensorFlow RFC](https://github.com/tensorflow/community/tree/master/rfcs)。参考结构需要项目化，不照搬生态审批。

平台交换依据：[Sketch 公开格式](https://developer.sketch.com/file-format/)、[sketch-constructor](https://github.com/amzn/sketch-constructor)。文件结构/回读、本地预览骨架、真实交互与最终前端还原分别验证；平台由用户手动导入并反馈；生成器版本/依赖/差异需锁定，不能只凭仓库说明报告运行成功。
