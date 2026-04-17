# Source Stack

## Назначение документа

Документ фиксирует канонический source-backed стек для 6-месячного пути `personal-lms`: какие источники являются backbone, какие используются как support, и как это ограничивает scope.

## Что зафиксировано

- Курс строится поверх curated внешних источников.
- Источники делятся на **core (backbone)** и **supplement (support)**.
- Любой источник работает через lesson wrapper и execution-процесс внутри LMS.

## Core backbone sources

### Foundation / Python

- Python Programming MOOC;
- Automate the Boring Stuff;
- Python docs / Python Tutorial.

### Developer workflow

- VS Code documentation;
- terminal / environments практики и официальные reference-материалы;
- GitHub Skills и источники по Git workflow.

### Backend / data / web

- MDN HTTP (базовые web/HTTP concepts);
- HTTPX documentation;
- SQLBolt;
- Python `sqlite3` documentation;
- FastAPI documentation/tutorial.

### Quality / reliability

- pytest documentation;
- Python logging documentation;
- CI fundamentals sources (GitHub Actions и базовые workflow references);
- debugging guides/reference для Python tooling.

### AI layer

- OpenAI quickstart;
- OpenAI SDK docs;
- OpenAI cookbook;
- Responses API docs;
- Structured Outputs;
- Function Calling;
- Moderation;
- Evals.

## Support sources (supplement)

Support-источники допускаются, если они:

- закрывают конкретный пробел текущего блока;
- не ломают приоритеты backbone;
- не превращают курс в каталог ссылок.

Типовые supplement-категории:

- точечные статьи/видео по debugging и tooling;
- примеры open-source репозиториев для чтения кода;
- справочные материалы по конкретным интеграциям.

## Критерий core vs supplement

Источник считается **core**, если он:

- покрывает ключевой участок pipeline;
- используется системно в нескольких модулях;
- поддерживает execution-first модель.

Источник считается **supplement**, если он:

- используется эпизодически;
- нужен для локального усиления понимания;
- не определяет структуру курса.

## Почему выбран именно этот набор

Набор выбран как минимально достаточный для связки:

- Python foundation;
- автоматизация и интеграции;
- backend/data практика;
- качество и надежность;
- прикладной AI layer.

Этот стек позволяет собирать результативные артефакты без перехода к избыточной multi-framework подготовке в первые 6 месяцев.

## Что сознательно не входит в первые 6 месяцев

- Углубленная computer science теория вне прямой прикладной пользы маршрута.
- Широкая frontend-специализация и сложные SPA-фреймворки.
- DevOps/SRE трек уровня production platform engineering.
- Enterprise-архитектуры и multi-tenant design как обязательная часть.
- Многофреймворочная backend-подготовка без необходимости для целевой ветки.

## Влияние на следующие этапы

- Authoring обязан явно маркировать источник как core или supplement.
- Curriculum hardening должен усиливать качество wrappers/tasks, а не бесконтрольно расширять список источников.
- Любое расширение источников после этого freeze требует отдельного decision record.
