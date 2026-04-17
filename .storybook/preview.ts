import type { Preview } from '@storybook/html';
import '../app/static/css/app.css';
import './storybook-preview.css';

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: 'personal-lms dark',
      values: [{ name: 'personal-lms dark', value: '#030405' }],
    },
    controls: {
      expanded: true,
      sort: 'requiredFirst',
    },
    layout: 'fullscreen',
    options: {
      storySort: {
        order: ['Shell', 'Dashboard', 'Course', 'Lesson', 'Recap'],
      },
    },
  },
};

export default preview;
