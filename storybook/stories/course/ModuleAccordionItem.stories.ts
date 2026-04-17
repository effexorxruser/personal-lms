import type { Meta, StoryObj } from '@storybook/html';
import { renderModuleAccordionItem } from '../../renderers/modules';
import type { UiState } from '../../renderers/cards';

type Args = { title: string; description: string; state: UiState; expanded: boolean; checkpointState: UiState };
const meta = { title: 'Course/ModuleAccordionItem', render: (args) => renderModuleAccordionItem(args), argTypes: { state: { control: 'select', options: ['in_progress', 'completed', 'needs_revision', 'checkpoint_pending', 'checkpoint_passed'] }, checkpointState: { control: 'select', options: ['checkpoint_pending', 'needs_revision', 'checkpoint_passed'] } }, args: { title: '1. Модуль 1: Основа backend', description: 'Базовые принципы backend-приложения.', state: 'checkpoint_pending', expanded: true, checkpointState: 'checkpoint_pending' } } satisfies Meta<Args>;
export default meta;
type Story = StoryObj<Args>;
export const Default: Story = {};
