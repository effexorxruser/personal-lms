import { storyShell } from './html';
import { renderTopbar } from './shell';
import { renderRecapSummary, UiState, stateLabel } from './cards';
import { renderExecutionRail } from './rails';
import { renderModuleAccordionItem } from './modules';

export function renderDashboardWorkspace(args: { checkpointState: UiState; blockerActive: boolean; density: 'compact' | 'normal' }): HTMLElement {
  const checkpointLabel = stateLabel(args.checkpointState);
  const content = `
    ${renderTopbar({ active: 'Главная', clockVisible: true, userAction: 'Выход' })}
    <section class="workspace-shell dashboard-workspace dashboard-workspace--resume">
      <div class="workspace-grid dashboard-resume-layout">
        <main class="workspace-pane dashboard-main dashboard-main--resume">
          <section class="dashboard-context-strip" aria-label="Текущий контекст обучения" style="--progress-value: 67%">
            <div class="dashboard-context-strip__lain" aria-hidden="true"></div>
            <div class="dashboard-context-strip__identity"><span class="dashboard-context-strip__user">effexorxruser</span><span>Python Backend + AI Learning</span></div>
            <div class="dashboard-context-strip__state"><span>Модуль: Основа backend</span><span>Checkpoint: ${checkpointLabel}</span></div>
            <div class="dashboard-context-strip__progress"><span class="progress-line"><span></span></span><strong>67%</strong></div>
          </section>
          <section class="dashboard-lms-grid">
            <article class="ui-card lms-summary-card"><p class="status-kicker">Прогресс</p><dl class="lms-lines"><div><dt>Курс</dt><dd>67%</dd></div><div><dt>Модуль</dt><dd>2/3 уроков</dd></div></dl></article>
            <article class="ui-card lms-summary-card lms-summary-card--actions"><p class="status-kicker">Следующие действия</p><p class="dashboard-action-state">Выполнение: ${checkpointLabel}</p><h2>Foundation artifact: CLI utility pack</h2><p class="rail-card__muted">${args.checkpointState === 'needs_revision' ? 'Нужно доработать checkpoint' : 'Готово к отправке checkpoint'}</p><div class="dashboard-action-row"><a class="btn btn--primary" href="#">Продолжить обучение</a><a class="btn btn--ghost" href="#">Карта курса</a></div></article>
            <article class="ui-card lms-summary-card"><p class="status-kicker">Итоги недели</p><p>2 уроков / 1 проверки</p><p class="rail-card__muted">блокеры: ${args.blockerActive ? 1 : 0}</p><a class="card-link" href="#">Открыть итоги</a></article>
          </section>
        </main>
      </div>
    </section>
  `;
  return storyShell(content, { page: 'dashboard' });
}

export function renderCourseMapWorkspace(args: { expanded: boolean; checkpointState: UiState }): HTMLElement {
  const content = `
    ${renderTopbar({ active: 'Курс', clockVisible: true, userAction: 'Выход' })}
    <section class="workspace-shell course-workspace">
      <main class="workspace-pane course-pane">
        <section class="ui-card course-summary-strip bg-course"><div class="hero__visual overlay-dark"></div><div class="course-summary-strip__body"><p class="eyebrow">Карта курса</p><h1>Python Backend + AI Learning</h1><div class="meta-row"><span class="meta-pill">Прогресс: 67%</span><span class="meta-pill">Модули как backbone</span></div></div></section>
        <section class="module-list" data-accordion="single">${renderModuleAccordionItem({ title: '1. Модуль 1: Основа backend', description: 'Базовые принципы backend-приложения.', state: args.checkpointState, expanded: args.expanded, checkpointState: args.checkpointState })}</section>
      </main>
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
          <section class="ui-card lesson-context-strip bg-lesson"><div class="hero__visual overlay-dark"></div><div><p class="eyebrow">Урок</p><h1>Урок 2: Структура backend</h1><p class="hero-copy">Спокойное чтение слева, выполнение и blockers справа.</p></div></section>
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
      <div class="workspace-toolbar"><nav class="workspace-tabs" data-tabs><button type="button" class="is-active" data-tab-target="recap-overview-panel">Обзор</button><button type="button" data-tab-target="recap-lessons">Уроки</button><button type="button" data-tab-target="recap-execution">Практика</button><button type="button" data-tab-target="recap-blockers">Блокеры</button><button type="button" data-tab-target="recap-focus">Фокус</button></nav></div>
      <main class="workspace-pane recap-pane">
        ${renderRecapSummary({ lessons: 3, submissions: 4, reviews: args.reviews, blockers: args.blockers })}
        <section class="recap-tab-panels"><article id="recap-overview-panel" class="ui-card recap-card" data-tab-panel><p class="status-kicker">Обзор</p><p>3 урока, 4 отправки, ${args.reviews} проверки, ${args.blockers} блокеров.</p></article><article id="recap-lessons" class="ui-card recap-card" data-tab-panel hidden><p class="status-kicker">Завершённые уроки</p><ul><li><strong>Урок 1: Введение в трек</strong><span>завершено 17.04</span></li><li><strong>Урок 2: Структура backend</strong><span>завершено 17.04</span></li></ul></article><article id="recap-execution" class="ui-card recap-card" data-tab-panel hidden><p class="status-kicker">Практика</p><ul><li><strong>Проверить структуру приложения</strong><span>review пройден</span></li></ul></article><article id="recap-blockers" class="ui-card recap-card" data-tab-panel hidden><p class="status-kicker">Блокеры</p><p>Активных блокеров: ${args.blockers}</p></article><article id="recap-focus" class="ui-card recap-card recap-card--focus" data-tab-panel hidden><p class="status-kicker">Следующий фокус</p><h2>Foundation artifact</h2><a class="btn btn--primary" href="#">Продолжить</a></article></section>
      </main>
    </section>
  `;
  return storyShell(content, { page: 'recap' });
}
