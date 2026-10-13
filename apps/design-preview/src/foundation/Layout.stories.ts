import type {Meta,StoryObj} from '@storybook/vue3-vite';
import RequirementsWorkspace from '../modules/requirements/RequirementsWorkspace.vue';
export default {title:'01 应用框架/整体布局',component:RequirementsWorkspace} satisfies Meta<typeof RequirementsWorkspace>;
export const Desktop:StoryObj<typeof RequirementsWorkspace>={name:'完整应用与导航',args:{initialRoute:'list',initialScenario:'normal'}};
