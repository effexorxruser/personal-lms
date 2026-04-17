import type { Meta, StoryObj } from '@storybook/html';
import { renderDashboardWorkspace } from '../../renderers/workspaces';
import type { UiState } from '../../renderers/cards';

type Args = { checkpointState: UiState; blockerActive: boolean; density: 'compact' | 'normal' };
const meta = { title: 'Dashboard/DashboardWorkspace', render: (args) => renderDashboardWorkspace(args), argTypes: { checkpointState: { control: 'select', options: ['checkpoint_pending', 'needs_revision', 'checkpoint_passed'] }, density: { control: 'select', options: ['compact', 'normal'] } }, args: { checkpointState: 'checkpoint_pending', blockerActive: false, density: 'normal' } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
