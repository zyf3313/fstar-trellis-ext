import type {Meta,StoryObj} from '@storybook/vue3-vite';
import Foundations from './Foundations.vue';
export default {title:'00 设计语言/风格与组件',component:Foundations} satisfies Meta<typeof Foundations>;
export const Baseline:StoryObj<typeof Foundations>={name:'视觉基线与组件状态'};
