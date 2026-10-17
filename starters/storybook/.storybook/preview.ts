import type { Preview } from '@storybook/vue3-vite'
import '../shared/explorer.css'
import '../shared/storybook.css'

document.documentElement.lang = 'zh-CN'

const preview: Preview = {
  parameters: {
    layout: 'fullscreen',
    controls: { expanded: true },
    options: {
      // Storybook 静态索引器要求排序规则内联；一致性检查负责与侧栏合同逐项核对。
      storySort: {
        includeNames: true,
        order: [
          '文档',
          ['案卷首页', '产品需求说明', '技术方案', '测试验收', '附件与格式说明', '*'],
          'UI 设计语言与资产',
          ['共享设计资产', 'UI 设计说明', '*'],
          '可交互原型',
          ['草稿', '评审中', '需修改', '已通过', '原型说明', '*'],
        ],
      },
    },
  },
}

export default preview
