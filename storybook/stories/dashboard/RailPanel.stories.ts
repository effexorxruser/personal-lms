import type { Meta, StoryObj } from '@storybook/html';
import { renderRailPanel } from '../../renderers/rails';

type Args = { kicker: string; title: string; body: string; linkLabel: string; density: 'compact' | 'normal' };
const meta = { title: 'Dashboard/RightRailPanel', render: (args) => renderRailPanel(args), argTypes: { density: { control: 'select', options: ['compact', 'normal'] } }, args: { kicker: 'Выполнение', title: 'Текущая задача', body: 'Submission ещё не отправлен', linkLabel: 'Открыть задачу', density: 'normal' } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
