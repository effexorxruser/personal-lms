export type Html = string;

export function escapeHtml(value: unknown): string {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

export function list(items: string[]): string {
  return items.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
}

export function storyShell(content: string, options: { page?: 'dashboard' | 'course' | 'lesson' | 'recap'; width?: string } = {}): HTMLElement {
  const root = document.createElement('div');
  root.innerHTML = `
    <div class="page-bg" aria-hidden="true">
      <div class="page-bg__base"></div>
      <div class="page-bg__image"></div>
      <div class="page-bg__glow"></div>
      <div class="page-bg__noise"></div>
    </div>
    <main class="page-shell app-shell" data-story-page="${options.page ?? 'dashboard'}" style="--shell-max-width: ${options.width ?? '1710px'}">
      <div class="page-stack app-shell__stack">${content}</div>
    </main>
  `;
  return root;
}
