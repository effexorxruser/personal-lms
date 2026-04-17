# Architecture Overview

## Назначение документа

Документ фиксирует высокоуровневые архитектурные решения MVP и объясняет, как архитектура обслуживает цель обучения.

## Архитектурный формат

`personal-lms` — web-first приложение.

Стартовый режим — локальный запуск. MVP не должен зависеть от сложного деплоя, VPS, Kubernetes, multi-service инфраструктуры или внешней managed-платформы.

## Зафиксированный стек

Для MVP зафиксирован стек:

- FastAPI;
- Jinja2;
- SQLite;
- Tailwind CSS;
- Alpine.js.

Текущие технические детали могут развиваться, но MVP-решения должны оставаться совместимыми с этим направлением.

## Почему FastAPI + Jinja2

FastAPI дает простой backend foundation:

- routes;
- forms/actions;
- API evolution позже;
- Python-first developer experience.

Jinja2 подходит MVP, потому что:

- не требует split frontend/backend;
- хорошо работает для server-rendered UI;
- уменьшает complexity;
- помогает быстрее строить учебный workflow.

## Почему SQLite

SQLite подходит MVP, потому что:

- простая локальная разработка;
- нет внешней database infrastructure;
- достаточно для single-user / trusted local MVP;
- снижает operational overhead.

PostgreSQL / Supabase могут быть рассмотрены позже, но не являются базой MVP.

## Миграции БД

В зависимостях проекта есть Alembic, но Alembic scaffold пока не создан: в репозитории нет `alembic.ini`, `env.py` и каталога версионированных migrations.

Текущий MVP-режим инициализации БД:

- модели описаны через SQLModel;
- `scripts/init_db.py` вызывает `SQLModel.metadata.create_all()`;
- новые таблицы для локальной SQLite базы создаются через повторный запуск `scripts/init_db.py`.

Это сознательно допустимо для текущего локального MVP, но является tech debt. Перед production-like deploy или перед сложными schema changes нужно добавить полноценный Alembic scaffold и перевести изменения схемы в версионированные migrations.

## Tailwind CSS и Alpine.js

Tailwind CSS и Alpine.js используются как легкий frontend layer.

Цель:

- не строить React-first frontend;
- не разделять приложение на отдельные frontend/backend проекты;
- сохранять простую server-rendered архитектуру;
- добавлять интерактивность только там, где она нужна.

## Хранение данных и контента

Принцип:

- контент хранить в файлах;
- runtime state хранить в БД.

Контент в файлах облегчает review, curation и подключение репозитория как source в GPT Projects. БД хранит состояние пользователя, progress, submissions и другие runtime-сущности.

## Platform hardening before curriculum scale-up

Перед массовым curriculum onboarding архитектура должна пройти platform hardening и выйти в authoring-ready состояние.

Фиксируется порядок:

- runtime/UX stabilization;
- authoring model readiness;
- ограниченный first curriculum pass;
- только после этого content scale-up.

Это снижает риск масштабирования нестабильной модели уроков и execution-flow.

## Authoring model readiness

С точки зрения архитектуры обязательна поддержка согласованной структуры:

- block;
- module;
- lesson;
- task;
- checkpoint (как evolvable сущность).

Checkpoint entity/model может быть добавлена как отдельная evolution-итерация, когда текущий runtime стабилизирован и требования явно закреплены.

## Практическое направление текущего этапа

Текущий прикладной фокус архитектурно совместим с веткой Telegram / automation / AI utility tools, но сама архитектура остается общей и не превращается в curriculum-специфичный документ.

## Локальный запуск

На старте приоритет — локальный запуск:

- проще разрабатывать;
- проще тестировать;
- меньше инфраструктурного шума;
- лучше соответствует personal LMS.

Будущий деплой возможен, но не должен диктовать MVP-архитектуру.

## Почему не React-first

React-first подход не выбран для MVP, потому что:

- увеличивает split frontend/backend complexity;
- требует больше build/tooling решений;
- отвлекает от learning workflow;
- не нужен для проверки основной продуктовой идеи.

## Почему не giant LMS

Giant LMS architecture не нужна, потому что MVP не решает задачи:

- multi-tenant платформы;
- публичного каталога курсов;
- enterprise администрирования;
- сложной роли преподавателей;
- social learning network.

Архитектура должна оставаться узкой и полезной для персонального обучения.

## Почему не desktop-first

Desktop-first и browser IDE не являются целями MVP.

Пользователь может использовать локальные dev tools, но платформа должна быть web-first orchestration layer: маршрут, progress, tasks, review и минимальный execution surface.

## Архитектура обслуживает обучение

Любое архитектурное усложнение должно проходить проверку:

- помогает ли оно пользователю учиться регулярнее;
- помогает ли оно выполнять задачи;
- помогает ли оно фиксировать progress;
- помогает ли оно снизить tutorial hell.

Если нет, решение не должно попадать в MVP.
