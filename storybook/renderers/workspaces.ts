import { storyShell } from './html';
import { renderTopbar, renderSectionNav } from './shell';
import { renderStatusCard, renderCheckpointPanel, renderRecapSummary, UiState } from './cards';
import { renderRailPanel, renderBlockerPanel, renderExecutionRail } from './rails';
import { renderModuleAccordionItem } from './modules';

export function renderDashboardWorkspace(args: { checkpointState: UiState; blockerActive: boolean; density: 'compact' | 'normal' }): HTMLElement {
  const content = `
    ${renderTopbar({ active: 'Главная', clockVisible: true, userAction: 'Выход' })}
    <section class="workspace-shell dashboard-workspace">
      <div class="workspace-toolbar">${renderSectionNav({ items: ['Центр', 'Сводка', 'Модули'] })}</div>
      <div class="workspace-grid dashboard-layout section-flow">
        <main class="workspace-pane dashboard-main">
          <section class="hero hero--compact hero--node bg-dashboard section-block">
            <div class="hero__visual overlay-dark"></div><div class="hero__ghost hero__ghost--lain"></div>
            <div class="hero__content hero__content--node">
              <div class="node-main"><p class="eyebrow">Узел обучения</p><h1>Личный центр обучения</h1><p class="hero-copy">Рабочий режим активен. Следующий шаг, состояние курса и прогресс доступны сразу.</p><a class="btn btn--primary" href="#">Продолжить обучение</a></div>
              <aside class="ui-card node-panel"><p class="node-panel__title">Текущее состояние</p><dl class="node-grid"><div><dt>Курс</dt><dd>Python Backend + AI Learning</dd></div><div><dt>Следующий шаг</dt><dd>Checkpoint artifact</dd></div><div><dt>Прогресс</dt><dd>67%</dd></div></dl></aside>
            </div>
          </section>
          <section class="card-grid card-grid--ops section-block">
            ${renderStatusCard({ title: 'Текущий курс', body: 'Python Backend + AI Learning', linkLabel: 'Открыть карту курса' })}
            ${renderStatusCard({ title: 'Следующий шаг', body: 'Foundation artifact: CLI utility pack', linkLabel: 'Открыть checkpoint', state: args.checkpointState })}
            ${renderStatusCard({ title: 'Прогресс недели', body: '67% завершено (2/3 уроков)' })}
          </section>
        </main>
        <aside class="workspace-pane workspace-rail dashboard-rail section-block">
          ${renderRailPanel({ kicker: 'Выполнение', title: 'Текущая задача', body: 'Нет активной задачи', density: args.density })}
          ${renderCheckpointPanel({ title: 'Foundation artifact: CLI utility pack', summary: 'Собрать checkpoint-артефакт.', description: 'Артефакт закрывает foundation module.', state: args.checkpointState, expanded: false })}
          ${renderBlockerPanel({ active: args.blockerActive, reason: 'Не понимаю задачу', note: 'Нужен план возврата.' })}
        </aside>
      </div>
    </section>
  `;
  return storyShell(content, { page: 'dashboard' });
}

export function renderCourseMapWorkspace(args: { expanded: boolean; checkpointState: UiState }): HTMLElement {
  const content = `
    ${renderTopbar({ active: 'Курс', clockVisible: true, userAction: 'Выход' })}
    <section class="workspace-shell course-workspace">
      <div class="workspace-grid workspace-grid--single">
        <main class="workspace-pane course-pane">
          <section class="hero hero--compact hero--course bg-course"><div class="hero__visual overlay-dark"></div><div class="hero__content"><p class="eyebrow">Карта курса</p><h1>Python Backend + AI Learning</h1><p class="hero-copy">Практический трек по Python backend и базовой AI-интеграции.</p></div></section>
          <section class="module-list" data-accordion="single">${renderModuleAccordionItem({ title: '1. Модуль 1: Основа backend', description: 'Базовые принципы backend-приложения.', state: args.checkpointState, expanded: args.expanded, checkpointState: args.checkpointState })}</section>
        </main>
      </div>
    </section>
  `;
  return storyShell(content, { page: 'course' });
}

export function renderLessonWorkspace(args: { state: UiState; reviewApproved: boolean }): HTMLElement {
  const content = `
    ${renderTopbar({ active: 'Уроки', clockVisible: true, userAction: 'Выход' })}
    <section class="workspace-shell lesson-shell">
      <div class="workspace-grid lesson-workspace">
        <main class="workspace-pane lesson-reading-pane">
          <section class="hero hero--compact hero--lesson bg-lesson"><div class="hero__visual overlay-dark"></div><div class="hero__ghost hero__ghost--lain-soft"></div><div class="hero__content"><p class="eyebrow">Режим урока</p><h1>Урок 2: Структура backend</h1><p class="hero-copy">Текущий каркас использует FastAPI, шаблоны Jinja2 и файловый контент.</p></div></section>
          <article class="markdown-body lesson-main"><h1>Структура backend</h1><p>Текущий каркас использует <strong>FastAPI</strong>, шаблоны Jinja2 и файловый контент.</p><p>Ключевой принцип: данные курса живут только в content/.</p></article>
        </main>
        <aside class="workspace-pane workspace-rail lesson-rail-pane">${renderExecutionRail({ taskTitle: 'Проверить структуру приложения', state: args.state, reviewApproved: args.reviewApproved })}</aside>
      </div>
    </section>
  `;
  return storyShell(content, { page: 'lesson' });
}

export function renderRecapWorkspace(args: { blockers: number; reviews: number }): HTMLElement {
  const content = `
    ${renderTopbar({ active: 'Итоги', clockVisible: true, userAction: 'Выход' })}
    <section class="workspace-shell recap-workspace">
      <div class="workspace-toolbar"><nav class="workspace-tabs" data-tabs><button type="button" class="is-active" data-tab-target="recap-lessons">Уроки</button><button type="button" data-tab-target="recap-execution">Практика</button><button type="button" data-tab-target="recap-blockers">Блокеры</button><button type="button" data-tab-target="recap-focus">Фокус</button></nav></div>
      <main class="workspace-pane recap-pane">
        ${renderRecapSummary({ lessons: 3, submissions: 4, reviews: args.reviews, blockers: args.blockers })}
        <section class="recap-tab-panels"><article id="recap-lessons" class="ui-card recap-card" data-tab-panel><p class="status-kicker">Завершённые уроки</p><ul><li><strong>Урок 1: Введение в трек</strong><span>завершено 17.04</span></li><li><strong>Урок 2: Структура backend</strong><span>завершено 17.04</span></li></ul></article><article id="recap-execution" class="ui-card recap-card" data-tab-panel hidden><p class="status-kicker">Практика</p><ul><li><strong>Проверить структуру приложения</strong><span>review пройден</span></li></ul></article><article id="recap-blockers" class="ui-card recap-card" data-tab-panel hidden><p class="status-kicker">Блокеры</p><p>Активных блокеров: ${args.blockers}</p></article><article id="recap-focus" class="ui-card recap-card recap-card--focus" data-tab-panel hidden><p class="status-kicker">Следующий фокус</p><h2>Foundation artifact</h2><a class="btn btn--primary" href="#">Продолжить</a></article></section>
      </main>
    </section>
  `;
  return storyShell(content, { page: 'recap' });
}
