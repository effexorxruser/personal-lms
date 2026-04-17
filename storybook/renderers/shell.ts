import { escapeHtml } from './html';

export interface TopbarArgs {
  active: 'Главная' | 'Курс' | 'Уроки' | 'Итоги';
  clockVisible: boolean;
  userAction: string;
}

export function renderTopbar(args: TopbarArgs): string {
  const items = [
    { label: 'Главная', href: '#dashboard' },
    { label: 'Курс', href: '#course' },
    { label: 'Уроки', href: '#lesson' },
    { label: 'Итоги', href: '#recap' },
  ];
  return `
    <header class="topbar">
      <div class="topbar__inner">
        <a class="topbar__brand" href="#">PERSONAL-LMS</a>
        <nav class="topbar__nav" aria-label="Основная навигация">
          ${items.map((item) => `<a class="topbar__link ${item.label === args.active ? 'is-active' : ''}" href="${item.href}">${item.label}</a>`).join('')}
        </nav>
        <div class="topbar__actions">
          ${args.clockVisible ? '<div class="topbar-clock"><span>МСК 06:50</span><span>TYO 12:50</span><span>NYC 23:50</span></div>' : ''}
          <a class="btn btn--ghost" href="#">${escapeHtml(args.userAction)}</a>
        </div>
      </div>
    </header>
  `;
}

export function renderSectionNav(args: { items: string[]; active?: string }): string {
  return `
    <nav class="section-nav" aria-label="Навигация по секциям">
      ${args.items.map((item) => `<a href="#${item.toLowerCase()}" class="${item === args.active ? 'is-active' : ''}">${escapeHtml(item)}</a>`).join('')}
    </nav>
  `;
}
