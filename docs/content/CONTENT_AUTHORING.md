# Content Authoring

Короткая инструкция для добавления учебного контента в `personal-lms`.

Нормативный контракт и практика: **[course_authoring/COURSE_PACK_CONTRACT.md](../course_authoring/COURSE_PACK_CONTRACT.md)** · **[COURSE_AUTHORING_GUIDE.md](../course_authoring/COURSE_AUTHORING_GUIDE.md)**. Границы MVP и заметки про контент/runtime — **[MVP_SCOPE.md](../product/MVP_SCOPE.md)**.

## 1) Структура content tree

```text
content/
  courses/
    <course-slug>/          # имя каталога = course.slug
      course.yml
      modules/
        <module-slug>/
          module.yml
          checkpoints/      # опционально: <slug>.checkpoint.yml (pack)
          lessons/
            <lesson-key>.md                    # legacy
            <lesson-key>/lesson.md             # канонический pack-layout
              tasks/                           # опционально: <slug>.task.yml
  tasks/
    <task-slug>.yml         # глобальный слой (альтернатива pack tasks/)
  checkpoints/
    <checkpoint-slug>.yml   # глобальный слой (альтернатива pack checkpoints/)
```

## 2) Быстрый старт через scaffold

```bash
source .venv/bin/activate

python scripts/scaffold_course.py \
  --slug my-backend-track \
  --title "My Backend Track" \
  --description "Практический курс по backend"

# Изолированный каркас с вложенным task/checkpoint в pack (без глобальных tasks/checkpoints):
# python scripts/scaffold_course.py ... --embed-pack-assets

python scripts/scaffold_module.py \
  --course-slug my-backend-track \
  --slug api-basics \
  --title "Модуль: API Basics" \
  --description "Базовые API-паттерны" \
  --first-lesson-key api-intro \
  --first-lesson-title "Урок: API Intro" \
  --first-lesson-summary "Первый шаг по API"

python scripts/scaffold_lesson.py \
  --course-slug my-backend-track \
  --module-slug api-basics \
  --key routing-basics \
  --title "Урок: Routing Basics" \
  --summary "Связать lesson flow и router" \
  --task-slug inspect-routing

python scripts/scaffold_task.py \
  --slug inspect-routing \
  --title "Проверить routing" \
  --summary "Найти ключевые маршруты" \
  --instructions "Укажи router и объясни его роль" \
  --with-terminal

python scripts/scaffold_checkpoint.py \
  --slug api-basics-checkpoint \
  --module-slug api-basics \
  --title "API Basics checkpoint" \
  --summary "Промежуточный артефакт" \
  --description "Собери небольшой проверяемый результат"
```

## 3) Как связать сущности

- `course.yml -> modules[]` должен содержать slug каждого модуля курса.
- `module.yml -> lessons[]` должен содержать key каждого урока модуля.
- `lesson front matter -> task_slug` (опционально) должен ссылаться на существующую задачу: `content/tasks/<slug>.yml` **или** pack-файл `lessons/<key>/tasks/<slug>.task.yml` (см. контракт).
- `checkpoint.yml -> module_slug` должен ссылаться на существующий модуль.

## 4) Обязательный preflight

Перед запуском приложения и перед commit:

```bash
source .venv/bin/activate
python scripts/validate_content.py
pytest
```

Если `validate_content.py` вернул non-zero exit code, контент считается broken. Предупреждения `[WARN]` (например отсутствие русскоязычных секций урока) не меняют код выхода и не блокируют CI, но их стоит устранять в новых материалах.

## 5) Частые ошибки

- Дубликаты `lesson.key`, `task.slug`, `checkpoint.slug`.
- Урок указан в `module.yml`, но нет ни `<lesson-key>.md`, ни `<lesson-key>/lesson.md`.
- Есть lesson-файл в папке, но его нет в `module.yml` (orphan).
- `task_slug` в уроке ссылается на несуществующую задачу.
- `module_slug` в checkpoint ссылается на несуществующий модуль.
- Пустой markdown body в уроке.
- Пустой `definition_of_done` в task/checkpoint.

## 6) Definition of Done для authoring

Контент готов, если:

1. Все файлы созданы через scaffold или вручную по той же схеме.
2. Все связи `course -> module -> lesson` и `lesson -> task`, `checkpoint -> module` валидны.
3. `python scripts/validate_content.py` проходит без ошибок.
4. `pytest` проходит без регрессий.
