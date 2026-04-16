---
key: backend-structure
title: "Урок 2: Структура backend"
summary: Как устроен текущий каркас приложения и где находится ответственность слоев.
objectives:
  - Понять роль routers/templates/services
  - Найти source of truth для контента
checklist:
  - Просмотреть content loader
  - Открыть lesson page в браузере
task_slug: inspect-app-layout
---
# Структура backend

Текущий каркас использует **FastAPI**, шаблоны Jinja2 и файловый контент.

Ключевой принцип: данные курса живут только в `content/`.
