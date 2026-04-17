import type { Meta, StoryObj } from '@storybook/html';
import { renderCheckpointPanel, type UiState } from '../../renderers/cards';

type Args = { title: string; summary: string; description: string; state: UiState; expanded: boolean };
const meta = { title: 'Dashboard/CheckpointPanel', render: (args) => renderCheckpointPanel(args), argTypes: { state: { control: 'select', options: ['checkpoint_pending', 'needs_revision', 'checkpoint_passed'] } }, args: { title: 'Foundation artifact: CLI utility pack', summary: 'Собрать checkpoint-артефакт.', description: 'Module-level artifact для portfolio-ready результата.', state: 'checkpoint_pending', expanded: true } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
