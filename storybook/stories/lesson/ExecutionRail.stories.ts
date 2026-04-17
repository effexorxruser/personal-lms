import type { Meta, StoryObj } from '@storybook/html';
import { renderExecutionRail } from '../../renderers/rails';
import type { UiState } from '../../renderers/cards';

type Args = { taskTitle: string; state: UiState; reviewApproved: boolean };
const meta = { title: 'Lesson/ExecutionRail', render: (args) => renderExecutionRail(args), argTypes: { state: { control: 'select', options: ['in_progress', 'needs_revision', 'completed'] } }, args: { taskTitle: 'Проверить структуру приложения', state: 'needs_revision', reviewApproved: false } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
