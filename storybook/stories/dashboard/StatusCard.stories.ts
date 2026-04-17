import type { Meta, StoryObj } from '@storybook/html';
import { renderStatusCard, type UiState } from '../../renderers/cards';

type Args = { title: string; body: string; linkLabel: string; state: UiState };
const meta = { title: 'Dashboard/StatusCard', render: (args) => renderStatusCard(args), argTypes: { state: { control: 'select', options: ['completed', 'in_progress', 'needs_revision', 'checkpoint_pending', 'checkpoint_passed'] } }, args: { title: 'Следующий шаг', body: 'Foundation artifact: CLI utility pack', linkLabel: 'Открыть checkpoint', state: 'checkpoint_pending' } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
