import type {Meta,StoryObj} from '@storybook/vue3-vite';
import design from '../../design/design.json';
import RequirementsWorkspace from './RequirementsWorkspace.vue';
const meta={title:'02 需求管理/F02 新建需求',component:RequirementsWorkspace,args:{initialRoute:'create'},parameters:{personal:{module:'M01',feature:'F02',version:design.version}}} satisfies Meta<typeof RequirementsWorkspace>;
export default meta;
type Story=StoryObj<typeof meta>;
export const Create:Story={name:'B06 填写需求'};
export const Invalid:Story={name:'B07 字段校验失败',args:{initialInvalid:true}};
export const Success:Story={name:'B08 提交成功',args:{initialRoute:'list',initialSuccess:true}};
