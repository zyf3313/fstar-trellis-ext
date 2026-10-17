import { addons } from 'storybook/manager-api'
import { create } from 'storybook/theming'
import { showAddonPanelForEntry } from './layout'

addons.setConfig({
  theme: create({
    base: 'light',
    brandTitle: '项目评审案卷',
    brandUrl: './?path=/story/dossier-home--overview',
    colorPrimary: '#10283d',
    colorSecondary: '#1b6b63',
    appBg: '#f3f5f4',
    appContentBg: '#fffdf8',
    appBorderColor: '#c9d3d6',
    barSelectedColor: '#1b6b63',
    textColor: '#263b4b',
    textMutedColor: '#5f707c',
  }),
  layoutCustomisations: {
    showPanel: showAddonPanelForEntry,
  },
})
