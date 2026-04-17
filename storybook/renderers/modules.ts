import { escapeHtml } from './html';
import { renderCheckpointPanel, stateLabel, statusClass, UiState } from './cards';

export function renderModuleAccordionItem(args: { title: string; description: string; state: UiState; expanded: boolean; checkpointState: UiState }): string {
  return `
    <details class="ui-card module-card module-details" ${args.expanded ? 'open' : ''}>
      <summary class="module-head">
        <h2>${escapeHtml(args.title)}</h2>
        <p>${escapeHtml(args.description)}</p>
        <span class="status-chip ${statusClass(args.state)}">Модуль: ${stateLabel(args.state)}</span>
      </summary>
      <ol class="lesson-list lesson-list--structured">
        <li class="lesson-row"><a class="inline-link" href="#">Урок 1: Введение в трек</a><span class="status-chip status-chip--success">Статус: завершён</span></li>
        <li class="lesson-row"><a class="inline-link" href="#">Урок 2: Структура backend</a><span class="status-chip status-chip--active">Статус: review пройден</span></li>
      </ol>
      ${renderCheckpointPanel({ title: 'Foundation artifact: CLI utility pack', summary: 'Собрать checkpoint-артефакт.', description: 'Module-level artifact для portfolio-ready результата.', state: args.checkpointState, expanded: true })}
    </details>
  `;
}
