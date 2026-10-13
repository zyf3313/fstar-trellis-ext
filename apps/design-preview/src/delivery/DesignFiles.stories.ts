import type {Meta,StoryObj} from '@storybook/vue3-vite';
import DesignFiles from './DesignFiles.vue';
export default {title:'03 设计文件与说明/图稿与导入',component:DesignFiles} satisfies Meta<typeof DesignFiles>;
export const Gallery:StoryObj<typeof DesignFiles>={name:'模块画廊与文件下载'};
