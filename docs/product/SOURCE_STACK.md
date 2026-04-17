# Source Stack

## Назначение документа

Документ фиксирует канонический source-backed стек для 6-месячного пути `personal-lms`: какие источники являются backbone, какие используются как support, и почему выбран именно такой состав.

## Что зафиксировано

- Курс строится поверх curated внешних источников.
- Источники делятся на **core (backbone)** и **supplement (support)**.
- Любой источник работает через lesson wrapper и execution-процесс внутри LMS.
- Стек выбран как прикладной и low-infra: от foundation к рабочим backend + AI артефактам.

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

Набор собран в последовательности, которая соответствует практическому pipeline курса:

1. foundation/docs/tooling формируют базу выполнения;
2. backend/data источники переводят базу в прикладные сервисные задачи;
3. quality/reliability источники фиксируют рабочий стандарт, чтобы артефакты были поддерживаемыми;
4. AI layer добавляется поверх уже работающего исполнения как усиление, а не как замена базовой инженерии.

Этот порядок уменьшает tutorial noise и поддерживает путь к наблюдаемым результатам.

## Архитектурные принципы стека

- **CLI-first**: terminal literacy нужна для автоматизации, Git workflow и reproducible execution.
- **Low-infra**: в первые 6 месяцев фокус на навыках разработки, а не на сложной инфраструктуре.
- **SQLite-first**: достаточно для локального single-user MVP и учебных backend сценариев.
- **AI-as-layer**: AI интегрируется после базовой backend/automation опоры для управляемого качества результата.

## Что сознательно не входит в первые 6 месяцев и почему

- Углубленная computer science теория вне прямой прикладной пользы маршрута (не ускоряет ранние рабочие артефакты).
- Широкая frontend-специализация и сложные SPA-фреймворки (уводит от backend + automation фокуса).
- DevOps/SRE трек уровня production platform engineering (избыточен для текущего этапа).
- Enterprise-архитектуры и multi-tenant design как обязательная часть (не соответствует MVP-ограничениям).
- Многофреймворочная backend-подготовка без необходимости (повышает когнитивную нагрузку без краткосрочной прикладной выгоды).

## Влияние на следующие этапы

- Authoring обязан явно маркировать источник как core или supplement.
- Curriculum hardening должен усиливать качество wrappers/tasks, а не бесконтрольно расширять список источников.
- Любое расширение источников после этого freeze требует отдельного decision record.
