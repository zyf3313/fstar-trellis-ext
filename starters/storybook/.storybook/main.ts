import type { StorybookConfig } from '@storybook/vue3-vite'
import vue from '@vitejs/plugin-vue'

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.ts'],
  staticDirs: ['../public'],
  framework: {
    name: '@storybook/vue3-vite',
    options: { docgen: false },
  },
  core: { disableTelemetry: true },
  async viteFinal(config) {
    return {
      ...config,
      // 静态目录只由 Storybook 复制，避免 Vite 并发复制 sources/ 产生目录竞争。
      publicDir: false,
      plugins: [...(config.plugins ?? []), vue()],
    }
  },
}

export default config
