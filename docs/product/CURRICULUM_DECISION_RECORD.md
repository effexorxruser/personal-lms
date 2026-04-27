# Curriculum Decision Record — Backend Developer (Python + AI)

## Статус

Accepted.

## Дата

2026-04-27.

## Контекст

`personal-lms` уже имеет execution-first архитектуру (lesson → task → submission → review), file-based content и runtime state в БД, но не имеет зафиксированного end-to-end curriculum уровня Backend Developer.

Нужно принять решение, которое:

- фиксирует 6-месячный путь от нуля до backend + AI;
- не расширяет scope платформы и не ломает guardrails;
- опирается на source-backed подход и curated backbone;
- гарантирует измеримые практические результаты и next step.

## Решение

Принято решение зафиксировать curriculum как 7 последовательных блоков (Block 0–6) с обязательными checkpoint-проектами и артефактами:

1. Block 0 — Technical English for Backend;
2. Block 1 — Environment + Git + Terminal + First Execution;
3. Block 2 — Python + Automation;
4. Block 3 — HTTP + APIs + SQLite;
5. Block 4 — FastAPI backend;
6. Block 5 — Testing + Debugging + CI;
7. Block 6 — AI integration (OpenAI / tools / structured outputs).

Для каждого блока обязательны:

- цель;
- навыки;
- core источники (только из `SOURCE_STACK.md`);
- execution-практика;
- демонстрируемый артефакт;
- ответ на вопрос "какая реальная ценность после блока";
- checkpoint мини-проект.

## Почему это решение

### 1) Соответствие продуктовой цели

Решение ведет к практическим backend + AI артефактам и снижает tutorial hell за счет обязательного execution на каждом шаге.

### 2) Совместимость с текущей архитектурой

Ничего не меняется в platform architecture: используется существующая модель content files + runtime state DB + submission/review pipeline.

### 3) Контроль scope

Маршрут фиксирован, low-infra и не уходит в multi-tenant/SPA/enterprise-перестройку.

### 4) Source-backed дисциплина

Backbone источники ограничены curated stack'ом и используются через wrapper, а не как неструктурированный каталог ссылок.

### 5) Russian-friendly реализация

Пользовательский слой остается русским, английские источники читаются целевыми фрагментами через technical English wrapper.

## Что сознательно НЕ делаем

- не пишем полный курс "с нуля" без внешнего backbone;
- не добавляем новые случайные источники как основу;
- не превращаем AI helper в автопилот;
- не добавляем сложную infra/devops ветку сверх MVP-фокуса;
- не размываем путь в "изучайте что угодно".

## Альтернативы, которые были отклонены

### A1. Свободный roadmap без фиксированных блоков

Отклонено: приводит к decision fatigue, потере next-step и росту tutorial hell.

### A2. Полностью авторский курс без source-backed модели

Отклонено: резко расширяет scope и снижает скорость получения практических результатов.

### A3. AI-first маршрут с ранним смещением в агентность

Отклонено: без backend-базы AI превращается в хрупкий слой и ухудшает инженерную устойчивость результата.

## Последствия решения

### Позитивные

- появляется единый, проверяемый маршрут на 24 недели;
- у каждого блока есть measurable outcomes и портфолио-артефакт;
- curriculum можно загружать в текущий authoring pipeline без архитектурных изменений.

### Риски

- риск перегруза источниками в блоках;
- риск ухода в theory-heavy уроки;
- риск "псевдопрактики" без строгого review.

### Митигации

- жесткий lesson wrapper: что читать / что игнорировать / что сделать;
- обязательный checkpoint после каждого блока;
- competency map и DoD-критерии для review;
- контроль "одно действие → один проверяемый результат".

## Правила внедрения (Implementation Guardrails)

1. Любой lesson без execution-задачи не считается готовым.
2. Любой блок без checkpoint-проекта не считается завершенным.
3. Любой новый источник вне `SOURCE_STACK.md` требует отдельного обоснования как supplement.
4. AI-фичи добавляются только поверх уже работающего backend-flow.
5. Progress закрывается только через submission + review, а не через факт чтения.

## Связанные документы

- `docs/product/CURRICULUM_ROADMAP.md`
- `docs/product/BACKEND_DEVELOPER_COMPETENCY_MAP.md`
- `docs/product/SOURCE_STACK.md`
- `docs/product/LEARNING_MODEL.md`
- `docs/product/AUTHORING_MODEL.md`

## Критерии валидации решения

Решение считается валидным, если одновременно выполнено:

1. Есть полный путь от нуля до backend + AI.
2. Каждый блок дает измеримый практический результат.
3. После каждого блока есть реальный мини-проект.
4. Нет расширения scope за рамки guardrails.
5. Пользователь всегда видит четкий next step.
6. Маршрут снижает tutorial hell за счет execution discipline.
7. Путь реалистично проходим в одиночку в режиме personal learning OS.
