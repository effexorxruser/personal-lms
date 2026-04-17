import type { Meta, StoryObj } from '@storybook/html';
import { renderRecapSummary } from '../../renderers/cards';

type Args = { lessons: number; submissions: number; reviews: number; blockers: number };
const meta = { title: 'Recap/RecapSummary', render: (args) => renderRecapSummary(args), args: { lessons: 3, submissions: 4, reviews: 4, blockers: 0 } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
