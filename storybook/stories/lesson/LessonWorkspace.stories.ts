import type { Meta, StoryObj } from '@storybook/html';
import { renderLessonWorkspace } from '../../renderers/workspaces';
import type { UiState } from '../../renderers/cards';

type Args = { state: UiState; reviewApproved: boolean };
const meta = { title: 'Lesson/LessonWorkspace', render: (args) => renderLessonWorkspace(args), argTypes: { state: { control: 'select', options: ['in_progress', 'needs_revision', 'completed'] } }, args: { state: 'needs_revision', reviewApproved: false } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
