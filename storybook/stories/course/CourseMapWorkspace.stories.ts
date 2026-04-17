import type { Meta, StoryObj } from '@storybook/html';
import { renderCourseMapWorkspace } from '../../renderers/workspaces';
import type { UiState } from '../../renderers/cards';

type Args = { expanded: boolean; checkpointState: UiState };
const meta = { title: 'Course/CourseMapWorkspace', render: (args) => renderCourseMapWorkspace(args), argTypes: { checkpointState: { control: 'select', options: ['checkpoint_pending', 'needs_revision', 'checkpoint_passed'] } }, args: { expanded: true, checkpointState: 'checkpoint_pending' } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
