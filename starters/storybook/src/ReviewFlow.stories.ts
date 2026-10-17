import type { Meta, StoryObj } from '@storybook/vue3-vite'
import ReviewPrototype from '../shared/components/ReviewPrototype.vue'

const meta = {
  id: 'review-flow',
  title: '可交互原型',
  component: ReviewPrototype,
  args: { explorerName: 'Storybook · 评审门户' },
} satisfies Meta<typeof ReviewPrototype>

export default meta
type Story = StoryObj<typeof meta>

export const Draft: Story = { name: '草稿', args: { initialState: 'draft' } }
export const Reviewing: Story = { name: '评审中', args: { initialState: 'reviewing' } }
export const Changes: Story = { name: '需修改', args: { initialState: 'changes' } }
export const Approved: Story = { name: '已通过', args: { initialState: 'approved' } }
