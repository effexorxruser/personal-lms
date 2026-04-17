# UI Baseline

## Назначение документа

Документ фиксирует текущий принятый UI baseline `personal-lms`.

Это внутренний source of truth для всех последующих UI-изменений. Если новая задача меняет визуальный слой, она должна сверяться с этим документом и с текущей token-based системой в `app/static/css/app.css`.

## Статус baseline

Текущий UI после финального dark matte glass pass считается основной и опорной визуальной системой проекта.

Baseline принят как:

- `dark-only` интерфейс;
- linux-like / Lain / hacker-workstation mood;
- matte glass terminal-window визуальная система;
- web-first LMS layout без redesign с нуля;
- token-based CSS foundation.

Это не временный эксперимент и не промежуточная тема. Все будущие UI-правки должны быть эволюционными.

## Основная визуальная формула

UI должен ощущаться как персональная рабочая станция для обучения Python backend + AI:

- почти черный shell background;
- graphite / charcoal поверхности;
- off-white readable typography;
- muted terminal green для state/prompt/status акцентов;
- muted blue для ссылок и navigation-like акцентов;
- muted yellow для progress/system акцентов;
- матовые прозрачные панели в духе terminal windows;
- Lain как эмоциональный ghost/presence layer.

Недопустимый вектор:

- generic SaaS LMS;
- bright cyan glow;
- toy-like glossy UI;
- белая/light theme без отдельного решения;
- случайные цветовые хаки вне token system.

## Theme decision

Для текущего этапа зафиксирована одна каноническая тема:

- `dark`

Light theme и theme switcher удалены из продуктового направления текущего этапа.

Нельзя возвращать:

- `light`;
- `default`;
- `wired` как theme name;
- UI-переключатель темы;
- multi-theme архитектуру.

Исключение: отдельное явно принятое product/design решение в будущем.

## Glass model

Текущая модель glass:

- матовая;
- прозрачная;
- terminal-window-like;
- без мыльного большого градиента;
- без кислотного свечения;
- с тонкими borders, inner highlights и restrained blur.

Glass допустим для:

- topbar;
- hero;
- compact cards;
- state panels;
- chips / pills / buttons;
- peripheral modules.

Glass не должен доминировать в:

- markdown body;
- long-form lesson content;
- main reading surfaces.

Reading surfaces должны оставаться solid and readable.

## Layout baseline

Текущий layout считается опорным:

- dashboard: hero + state panel + нижние status cards + right-side peripheral rail;
- course page: hero + module surfaces;
- lesson page: hero + readable content + supporting side panels;
- topbar: compact linux-like navigation.

Допустимы небольшие эволюционные изменения:

- перераспределение secondary modules;
- уточнение spacing;
- уточнение glass/material tokens;
- добавление небольших peripheral modules в существующий rail.

Недопустимы без отдельной задачи:

- redesign с нуля;
- смена navigation model;
- превращение dashboard в другую информационную архитектуру;
- замена текущего visual language на generic LMS или SaaS dashboard.

## Dashboard side rail

Правая боковая секция dashboard является принятой зоной для малых системных модулей.

Текущий модуль:

- `Системное время`;
- вертикальный список `MOW / TYO / NYC`;
- compact matte glass surface.

В будущем сюда можно добавлять только небольшие supporting modules, которые не расширяют product scope и не конкурируют с основным next step.

## Lain integration

Lain зафиксирована как subtle emotional presence.

Правила:

- Lain может быть ghost layer / side visual presence;
- Lain не должна перекрывать основной текст;
- Lain не должна становиться full-page poster;
- Lain не используется как markdown/readable background;
- opacity, masking и position должны поддерживать читаемость.

Цель: Lain должна чувствоваться как часть dev environment, а не как отдельный декоративный баннер.

## Asset roles

Текущие visual assets используются по ролям:

- shell background: linux terminal/workstation atmosphere;
- dashboard hero: AI / terminal / node visual layer;
- course hero: industrial topology / system-map feeling;
- lesson hero: quieter industrial/system visual layer;
- Lain images: emotional ghost / side presence layer.

Новые изображения нельзя добавлять случайно. Если asset меняется, нужно обновить роль или объяснить, почему новый asset лучше поддерживает baseline.

## CSS token contract

`app/static/css/app.css` является текущим design-token contract.

Новые UI-изменения должны идти через:

1. foundation tokens;
2. theme/base tokens;
3. semantic surface/text/border/accent tokens;
4. component tokens;
5. page-specific rules только при необходимости.

Запрещено:

- добавлять случайные raw colors в component rules;
- локально перекрашивать отдельные карточки без token;
- обходить существующие surface/accent/border tokens;
- возвращать multi-theme логику;
- менять visual direction через точечные хаки.

## Typography baseline

Текущий baseline использует mono-first stack:

- JetBrains Mono;
- Ubuntu Mono;
- SF Mono;
- Cascadia Mono;
- Fira Code;
- fallback monospace.

Цель: linux terminal / workstation character без потери читаемости.

## UI change checklist

Перед принятием UI-изменения проверить:

- dark-only режим сохранен;
- theme switcher не возвращен;
- текущий linux-like / Lain / hacker-workstation mood сохранен;
- glass остается matte / terminal-window-like;
- нет дешевого cyan glow;
- нет generic SaaS styling;
- текст читается в hero/cards/panels;
- markdown body остается solid/readable;
- Lain/background не перекрывают контент;
- изменения сделаны через tokens, если это color/surface/material правки;
- `git diff --check` проходит;
- `.venv/bin/python -m pytest` проходит.

## Что не зафиксировано

Пока не зафиксировано:

- финальная визуальная спецификация будущего terminal-like execution surface;
- набор будущих peripheral modules для dashboard rail;
- визуальные правила для еще не созданных дополнительных треков;
- полный component library за пределами текущих страниц.
