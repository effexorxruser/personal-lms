import type { StorybookConfig } from '@storybook/html-vite';

const config: StorybookConfig = {
  framework: '@storybook/html-vite',
  stories: ['../storybook/stories/**/*.stories.@(ts|js|mdx)'],
  addons: ['@storybook/addon-essentials'],
  staticDirs: [{ from: '../app/static', to: '/static' }],
  docs: { autodocs: 'tag' },
  viteFinal: async (config) => ({
    ...config,
    publicDir: false,
  }),
};

export default config;
