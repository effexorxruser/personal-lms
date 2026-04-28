# UI Baseline

## Назначение документа

Документ фиксирует текущий принятый UI baseline `personal-lms`.

Это внутренний source of truth для всех последующих UI-изменений. Если новая задача меняет визуальный слой, она должна сверяться с этим документом и с текущей token-based системой в `app/static/css/app.css`.

## Статус baseline

Текущий UI после финального dark matte glass pass считается основной и опорной визуальной системой проекта.

Baseline принят как:

- `dark-first` интерфейс (default `lain`);
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

Текущий baseline поддерживает controlled multi-theme customization через UI settings panel.

Разрешенные runtime themes:

- `lain` (default)
- `vanilla-dark`
- `vanilla-light`

Утвержденная asset-map (2026-04):

- `vanilla-dark`
 - dashboard: `SHELL BACKGROUND-1.png`
 - course: `COURSE HERO (industrial topology)-1.png`
 - lesson: ровный темный фон (без texture asset)
 - recap: `DASHBOARD HERO (terminal  linux hybrid)-2.png`
- `vanilla-light`
 - dashboard: `SHELL BACKGROUND-2.png`
 - course: `COURSE HERO (system map  backend structure)-1.png`
 - lesson: ровный светлый фон (без texture asset)
 - recap: `SHELL BACKGROUND (ALT — linux workspace)-2.png`
- `lain`
 - dashboard: `SHELL BACKGROUND-2.png`
 - course: `COURSE HERO (industrial topology)-2.png`
 - lesson: ровный темный фон (без texture asset)
 - recap: `SHELL BACKGROUND (ALT — linux workspace)-1.png`
 - ambient overlay: `lain-image-4.jpg` + `lain-image-1.jpg`
 - helper avatar: `lain-image-6.png`

Дополнительно:

- переключатель `glass on/off`;
- хранение пользовательских предпочтений на клиенте (localStorage);
- без отдельной server-side настройки темы в MVP.
- login page визуально синхронизирована с default `lain` стартовым состоянием.

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

## Final UI closure (2026-04)

Финальный вектор зафиксирован как:

- `iOS-26-inspired glass` material language;
- `Lain anime` emotional ambient layer;
- `linux-like` интерфейсная дисциплина и контраст;
- `balanced performance` как обязательное ограничение.

Это означает:

- glass должен выглядеть «дорого», но не превращать страницу в декоративный шум;
- динамика должна быть мягкой, короткой и контекстной;
- canvas/webgl-декор допустим только как enhancement для ambient/hero зон;
- SSR-поток, execution-first UX и читаемость контента остаются приоритетом.

### Material levels (обязательный контракт)

В `app/static/css/app.css` закреплены уровни glass-материала:

- `glass-level-1`: context strips и верхние системные поверхности;
- `glass-level-2`: базовые карты/панели;
- `glass-level-3`: фокусные action-панели.

Для каждого уровня обязательно держать:

- fill opacity/gradient;
- edge light + edge shadow;
- blur/saturation;
- specular/reflection overlays.

### Motion and performance contract

Motion допускается только в виде micro-interactions:

- hover depth shift;
- subtle button feedback;
- мягкий context highlight.

Ограничения:

- обязательная поддержка `prefers-reduced-motion`;
- на mobile/low-power устройствах heavy motion отключается;
- canvas ambient не должен блокировать input/scroll и не должен быть dependency для UX.

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
- замена текущего visual language на generic LMS или neutral SaaS dashboard.

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

## Lain Helper UI baseline (v1.0)

UI helper зафиксирован как часть baseline:

- floating capsule launcher в правом нижнем углу;
- compact popover panel с quick actions, сократическим toggle и историей;
- онлайн/ожидание (`online/thinking`) индикатор;
- theme-aware styling для `lain`, `vanilla-dark`, `vanilla-light`;
- panel не должна перекрывать основной next-step контент и должна оставаться периферийной.

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

Разрешено в рамках customization UI:

- менять `data-theme` и `data-glass` на уровне `html`;
- переопределять только токены темы (surface/text/accent), не ломая component contract.

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

- dark-first default (`lain`) сохранен;
- theme switcher остается рабочим;
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
