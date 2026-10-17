import type { Meta, StoryObj } from '@storybook/vue3-vite'
import DesignLanguage from '../shared/components/DesignLanguage.vue'

const meta = {
  id: 'design-language',
  title: 'UI 设计语言与资产',
  component: DesignLanguage,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof DesignLanguage>

export default meta
type Story = StoryObj<typeof meta>

export const Tokens: Story = { name: '共享设计资产' }
