---
key: backend-structure
title: "Урок 2: Структура backend"
summary: Где находятся ключевые backend-слои и как они связаны в рабочем потоке.
objectives:
  - Увидеть роли routers, services и templates
  - Найти source of truth для file-based контента
checklist:
  - Просмотреть content loader и registry
  - Сопоставить lesson page с backend-роутом
task_slug: inspect-app-layout
---
# Структура backend

Текущий baseline использует **FastAPI**, шаблоны Jinja2 и file-based контент.

Ключевой принцип: контент хранится в `content/`, runtime state хранится в БД.
