# Руководство по авторингу курса

Практические шаги для file-based курса в `personal-lms`. Нормативный контракт: [COURSE_PACK_CONTRACT.md](COURSE_PACK_CONTRACT.md).

## Быстрый старт: каркас курса

Из корня репозитория:

```bash
python scripts/scaffold_course.py \
  --slug my-course \
  --title "Мой курс" \
  --description "Краткое описание." \
  --starter-module-slug foundation \
  --starter-lesson-key intro
```

Скрипт создаёт каталог курса, стартовый модуль, уроки в каноническом layout (`lessons/<key>/lesson.md`), вложенные `tasks/` и `checkpoints/` при необходимости, поле `schema_version: 1`.

Для полного прохождения валидации в изолированной папке укажите `--content-root`, а также создайте задачи/чекпоинты через `scripts/scaffold_task.py` / `scripts/scaffold_checkpoint.py` с `--task-root` / `--checkpoint-root`, либо держите их внутри пакета (`.task.yml` / `.checkpoint.yml`), как в контракте.

## Модули

1. Создайте `content/courses/<course-slug>/modules/<module-slug>/module.yml`.
2. Убедитесь, что `slug` в YAML совпадает с `<module-slug>`.
3. Добавьте slug модуля в список `modules` в `course.yml` (порядок = порядок в каталоге).
4. Укажите `checkpoint` на существующий чекпоинт (файл в пакете или в `content/checkpoints/`).

Удобно: `python scripts/scaffold_module.py --course-slug ... --slug ...` (см. `--help`).

## Уроки

1. Канонически: `lessons/<lesson-key>/lesson.md` с YAML front matter (`key`, `title`, `summary`, `objectives`, `source_ids`, опционально `task_slug`).
2. Legacy: один файл `lessons/<lesson-key>.md` — по-прежнему поддерживается.
3. Добавьте ключ урока в `module.yml` в `lessons` в желаемом порядке (минимум два урока на модуль).
4. Включите baseline-секции в теле урока (см. контракт); для новых материалов добавьте русскоязычные секции — иначе валидатор выдаст предупреждения.

`python scripts/scaffold_lesson.py --course-slug ... --module-slug ... --key ...` — создаёт урок и дописывает его в `module.lessons`.

## Задачи

- Глобально: `content/tasks/<slug>.yml` + ссылка `task_slug` в уроке при необходимости.
- В пакете: `lessons/<lesson-key>/tasks/<slug>.task.yml` (тот же формат полей, что и у глобальной задачи).

`python scripts/scaffold_task.py --slug ... --task-root ...`

## Чекпоинты

- Глобально: `content/checkpoints/<slug>.yml`.
- В пакете: `modules/<module-slug>/checkpoints/<slug>.checkpoint.yml`.

Поле `module_slug` в чекпоинте должно указывать на существующий модуль.

## Валидация

```bash
python scripts/validate_content.py
```

С фиксированными корнями (например временный каталог в тестах):

```bash
python scripts/validate_content.py \
  --content-root /path/to/courses \
  --task-root /path/to/tasks \
  --checkpoint-root /path/to/checkpoints \
  --source-root /path/to/sources
```

Сообщения с префиксами `[OK]`, `[WARN]`, `[ERROR]`. Код выхода 1 только при ошибках.

## Локальная проверка в приложении

Запустите сервер по инструкции проекта (например `scripts/start_local.sh` или `uvicorn`), откройте каталог курсов и уроки в браузере. Новый курс появится после успешной валидации и перезагрузки процесса (кэш реестра контента сбрасывается между запусками).

## Где смотреть примеры

Минимальные примеры манифестов: [docs/examples/](../examples/).
