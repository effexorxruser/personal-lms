import type { Meta, StoryObj } from '@storybook/html';
import { renderRecapWorkspace } from '../../renderers/workspaces';

type Args = { blockers: number; reviews: number };
const meta = { title: 'Recap/RecapWorkspace', render: (args) => renderRecapWorkspace(args), args: { blockers: 0, reviews: 4 } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
