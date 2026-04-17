import { escapeHtml, list } from './html';

export type UiState = 'completed' | 'in_progress' | 'needs_revision' | 'checkpoint_pending' | 'checkpoint_passed';

export function statusClass(state: UiState): string {
  if (state === 'completed' || state === 'checkpoint_passed') return 'status-chip--success';
  if (state === 'needs_revision') return 'status-chip--revision';
  return 'status-chip--active';
}

export function stateLabel(state: UiState): string {
  return {
    completed: 'завершён',
    in_progress: 'в процессе',
    needs_revision: 'требует доработки',
    checkpoint_pending: 'checkpoint ожидает отправки',
    checkpoint_passed: 'checkpoint пройден',
  }[state];
}

export function renderStatusCard(args: { title: string; body: string; linkLabel?: string; state?: UiState }): string {
  return `
    <article class="ui-card status-card ${args.state === 'in_progress' ? 'status-card--focus' : ''}">
      <p class="status-kicker">${escapeHtml(args.title)}</p>
      <p>${escapeHtml(args.body)}</p>
      ${args.state ? `<span class="status-chip ${statusClass(args.state)}">${stateLabel(args.state)}</span>` : ''}
      ${args.linkLabel ? `<a class="card-link" href="#">${escapeHtml(args.linkLabel)}</a>` : ''}
    </article>
  `;
}

export function renderCheckpointPanel(args: {
  title: string;
  summary: string;
  description: string;
  state: UiState;
  expanded: boolean;
}): string {
  const requirements = ['README содержит запуск', 'Есть demo path', 'Артефакт доступен для review'];
  const portfolio = ['Можно показать в GitHub', 'Понятен сценарий использования'];
  return `
    <section class="checkpoint-panel">
      <div class="checkpoint-panel__head">
        <p class="status-kicker">Checkpoint artifact</p>
        <span class="status-chip ${statusClass(args.state)}">${stateLabel(args.state)}</span>
      </div>
      <h3>${escapeHtml(args.title)}</h3>
      <p>${escapeHtml(args.summary)}</p>
      <p class="rail-card__muted">${escapeHtml(args.description)}</p>
      ${args.expanded ? `
        <div class="checkpoint-grid">
          <div><h4>Требования</h4><ul>${list(requirements)}</ul></div>
          <div><h4>Portfolio ожидания</h4><ul>${list(portfolio)}</ul></div>
        </div>
        <form class="task-form checkpoint-form">
          <label>Ссылка на репозиторий</label>
          <input type="url" placeholder="https://github.com/..." />
          <button type="button" class="btn btn--primary">Отправить checkpoint</button>
        </form>
      ` : ''}
    </section>
  `;
}

export function renderRecapSummary(args: { lessons: number; submissions: number; reviews: number; blockers: number }): string {
  return `
    <section class="hero hero--compact bg-dashboard">
      <div class="hero__visual overlay-dark" aria-hidden="true"></div>
      <div class="hero__content">
        <p class="eyebrow">Итоги недели</p>
        <h1>Итоги последних 7 дней</h1>
        <p class="hero-copy">Итоги собираются из реальных учебных событий: завершённые уроки, отправки, проверки и моменты, где ты застрял.</p>
        <div class="meta-row">
          <span class="meta-pill">Уроки: ${args.lessons}</span>
          <span class="meta-pill">Отправки: ${args.submissions}</span>
          <span class="meta-pill">Проверки: ${args.reviews}</span>
          <span class="meta-pill">Блокеры: ${args.blockers}</span>
        </div>
      </div>
    </section>
  `;
}
