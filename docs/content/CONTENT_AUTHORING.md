# Content Authoring

Короткая инструкция для добавления учебного контента в `personal-lms`.

## 1) Структура content tree

```text
content/
  courses/
    <course-slug>/
      course.yml
      modules/
        <module-slug>/
          module.yml
          lessons/
            <lesson-key>.md
  tasks/
    <task-slug>.yml
  checkpoints/
    <checkpoint-slug>.yml
```

## 2) Быстрый старт через scaffold

```bash
source .venv/bin/activate

python scripts/scaffold_course.py \
  --slug my-backend-track \
  --title "My Backend Track" \
  --description "Практический курс по backend"

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
- `lesson front matter -> task_slug` (опционально) должен ссылаться на существующий `content/tasks/*.yml`.
- `checkpoint.yml -> module_slug` должен ссылаться на существующий модуль.

## 4) Обязательный preflight

Перед запуском приложения и перед commit:

```bash
source .venv/bin/activate
python scripts/validate_content.py
pytest
```

Если `validate_content.py` вернул non-zero exit code, контент считается broken.

## 5) Частые ошибки

- Дубликаты `lesson.key`, `task.slug`, `checkpoint.slug`.
- Урок указан в `module.yml`, но файла `<lesson-key>.md` нет.
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
