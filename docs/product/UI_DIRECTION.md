# UI Direction

## Назначение документа

Документ фиксирует визуальное и UX-направление `personal-lms`, чтобы будущие изменения интерфейса не превращали продукт в generic LMS.

## Визуальное направление

Согласованное направление:

**linux-like / anime Lain / hacker-workstation inspired**.

Это не декоративный скин поверх LMS. Направление должно поддерживать ощущение персональной dev learning environment.

## Зачем такой UI

UI должен давать:

- характер продукта;
- погружение;
- эмоциональную связность с обучением;
- ощущение terminal culture и dev environment;
- визуальную мотивацию возвращаться к практике.

При этом интерфейс обязан оставаться функциональным, читаемым и спокойным.

## Как это сочетается с LMS-функцией

LMS-функция остается главной:

- маршрут;
- progress;
- tasks;
- submissions;
- review;
- stuck flow;
- weekly recap.

Визуальный стиль должен усиливать эти действия, а не конкурировать с ними.

## Обязательные UX-паттерны

Интерфейс должен поддерживать:

- понятный next step;
- видимый текущий progress;
- быстрый переход к текущему уроку;
- читаемую карту курса;
- читаемую страницу урока;
- отдельные supporting panels;
- clear state для задач и review;
- terminal-like execution surface там, где это помогает обучению.

## Lain presence

Lain — это subtle emotional presence, а не основной фон и не центральный баннер.

Допустимо:

- ghost layer в hero;
- controlled decorative insert;
- low/medium opacity;
- placement вне основной зоны чтения.

Недопустимо:

- перекрывать основной текст;
- превращать страницу в постер;
- использовать Lain как фон markdown body;
- ставить персонажа в центр как главный объект интерфейса.

## Как избежать визуального шума

Нужно избегать:

- дешевого glow;
- чрезмерного blur;
- кислотного cyan SaaS-вида;
- перегруженных фонов под текстом;
- декоративных элементов без функции;
- слишком сильных anime references в reading area.

Длинные текстовые поверхности должны оставаться solid and readable.

## Минимальный встроенный терминал

В MVP согласован минимальный встроенный терминал / terminal-like execution surface.

Его роль:

- связать обучение с execution;
- поддержать CLI literacy;
- дать ощущение работы в dev environment;
- позволить выполнять маленькие учебные действия внутри платформы.

Это не полноценная IDE и не замена VS Code.

## Темизация

Текущее направление поддерживает theme customization без смены архитектуры SSR.

Базовые пользовательские темы:

- `vanilla-dark`
- `vanilla-light`
- `lain`

Также поддерживается системный переключатель glass-material:

- `glass on`
- `glass off`

## Liquid glass implementation track

Для текущего этапа принят `hybrid_canvas` подход:

- основа: CSS token-based glass (fill/edge/specular/blur);
- enhancement: легкий Canvas ambient только для hero/background зон;
- перф-контур: отключение при `prefers-reduced-motion` и fallback без Canvas.

## Принятый UI baseline

Текущий dark-first UI (default `lain`) после финального matte glass cleanup pass считается принятой опорной визуальной системой проекта.

Канонический baseline описан в [`UI_BASELINE.md`](UI_BASELINE.md).

Все будущие UI-изменения должны:

- сохранять linux-like / anime Lain / hacker-workstation mood в default-настройке;
- использовать существующую token-based систему в `app/static/css/app.css`;
- сохранять linux-like / anime Lain / hacker-workstation mood;
- развивать текущий matte glass terminal-window material, а не заменять его новым стилем;
- не возвращать generic SaaS LMS styling;
- не превращать тему в нечитабельный декоративный режим;
- не ухудшать читаемость markdown body и long-form lesson content.

Текущий dashboard right-side rail считается допустимой зоной для небольших supporting modules. Он не должен превращаться в отдельную платформенную панель или расширять scope MVP.

## Не зафиксировано

- Точный visual system spec для всех будущих компонентов.
- Финальная реализация terminal-like surface.
- Полный набор иллюстраций для всех будущих треков.
