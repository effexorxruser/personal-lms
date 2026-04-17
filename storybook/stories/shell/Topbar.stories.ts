import type { Meta, StoryObj } from '@storybook/html';
import { renderTopbar, type TopbarArgs } from '../../renderers/shell';

const meta = { title: 'Shell/Topbar', render: (args) => renderTopbar(args), argTypes: { active: { control: 'select', options: ['Главная', 'Курс', 'Уроки', 'Итоги'] } }, args: { active: 'Главная', clockVisible: true, userAction: 'Выход' } } satisfies Meta<TopbarArgs>;
export default meta;
type Story = StoryObj<TopbarArgs>;
export const Default: Story = {};
