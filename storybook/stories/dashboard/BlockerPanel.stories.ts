import type { Meta, StoryObj } from '@storybook/html';
import { renderBlockerPanel } from '../../renderers/rails';

type Args = { active: boolean; reason: string; note: string };
const meta = { title: 'Dashboard/BlockerPanel', render: (args) => renderBlockerPanel(args), args: { active: true, reason: 'Не понимаю review', note: 'Нужен план возврата.' } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Active: Story = {};
export const Inactive: Story = { args: { active: false } };
