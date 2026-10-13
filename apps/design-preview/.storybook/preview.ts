import type {Preview} from '@storybook/vue3-vite';
import '../src/design/tokens.css';
import '../src/styles.css';
const preview: Preview={
  parameters:{layout:'fullscreen',options:{storySort:{order:['00 设计语言','01 应用框架','02 需求管理','03 设计文件与说明']}}},
};
export default preview;
