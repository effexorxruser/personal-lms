import { escapeHtml } from './html';
import { stateLabel, statusClass, UiState } from './cards';

export function renderRailPanel(args: { kicker: string; title: string; body: string; linkLabel?: string; density: 'compact' | 'normal' }): string {
  return `
    <section class="ui-card rail-card ${args.density === 'compact' ? 'rail-card--compact' : ''}">
      <p class="status-kicker">${escapeHtml(args.kicker)}</p>
      <h2>${escapeHtml(args.title)}</h2>
      <p>${escapeHtml(args.body)}</p>
      ${args.linkLabel ? `<a class="card-link" href="#">${escapeHtml(args.linkLabel)}</a>` : ''}
    </section>
  `;
}

export function renderBlockerPanel(args: { active: boolean; reason: string; note: string }): string {
  return `
    <article class="ui-card lesson-card stuck-panel">
      <p class="lesson-nav-title">Блокер</p>
      <h2>${args.active ? 'Я застрял' : 'Блокер не активен'}</h2>
      ${args.active ? `<p>Активный блокер: ${escapeHtml(args.reason)}</p><p class="rail-card__muted">${escapeHtml(args.note)}</p><button class="btn btn--ghost" type="button">Снять блокер</button>` : '<p class="rail-card__muted">Если застрянешь, отметь это на странице урока.</p>'}
    </article>
  `;
}

export function renderExecutionRail(args: { taskTitle: string; state: UiState; reviewApproved: boolean }): string {
  return `
    <aside class="lesson-side">
      <nav class="ui-card lesson-jump-panel lesson-side-dock">
        <p class="lesson-nav-title">Быстрые переходы</p>
        <div class="lesson-jumps"><a href="#">Задача</a><a href="#">Проверка</a><a href="#">Блокер</a><a href="#">Дальше</a></div>
      </nav>
      <article class="ui-card lesson-card task-panel">
        <p class="lesson-nav-title">Связанная задача</p>
        <h2>${escapeHtml(args.taskTitle)}</h2>
        <dl class="task-meta"><div><dt>Проверка</dt><dd>${stateLabel(args.state)}</dd></div></dl>
        <div class="task-review ${args.reviewApproved ? 'task-review--approved' : 'task-review--revision'}">
          <p class="status-kicker">Результат проверки</p>
          <p>${args.reviewApproved ? 'Базовая проверка пройдена.' : 'Нужна доработка результата.'}</p>
        </div>
        <span class="status-chip ${statusClass(args.state)}">${stateLabel(args.state)}</span>
      </article>
      ${renderBlockerPanel({ active: args.state === 'needs_revision', reason: 'Не понимаю review', note: 'Нужно уточнить критерии готовности.' })}
    </aside>
  `;
}
