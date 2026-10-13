import type {Meta,StoryObj} from '@storybook/vue3-vite';
import Documentation from './Documentation.vue';
export default {title:'03 设计文件与说明/中文 PRD 与 TDD',component:Documentation} satisfies Meta<typeof Documentation>;
export const Docs:StoryObj<typeof Documentation>={name:'业务需求与技术方案'};
