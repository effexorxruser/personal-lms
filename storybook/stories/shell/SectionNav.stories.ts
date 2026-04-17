import type { Meta, StoryObj } from '@storybook/html';
import { renderSectionNav } from '../../renderers/shell';

type Args = { active: string };
const meta = { title: 'Shell/SectionNav', render: (args) => renderSectionNav({ items: ['Центр', 'Сводка', 'Модули'], active: args.active }), argTypes: { active: { control: 'select', options: ['Центр', 'Сводка', 'Модули'] } }, args: { active: 'Центр' } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
