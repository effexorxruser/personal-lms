---
key: foundation-real-git-loop
title: "Урок 3: Минимальный Git/GitHub цикл"
summary: Закрыть базовый цикл `status -> add -> commit -> push` и зафиксировать артефакт в GitHub.
objectives:
  - Стабильно выполнить локальный Git commit cycle
  - Опубликовать результат в удалённый GitHub-репозиторий
checklist:
  - Пройти выбранные разделы Git Book и GitHub Hello World
  - Сделать минимум один осмысленный commit с сообщением
  - Отправить ссылку на commit или PR в task submission
task_slug: foundation-git-github-cycle
---
# Зачем этот шаг в маршруте

Без Git-цикла execution-first маршрут не масштабируется: нужен проверяемый след изменений и внешний артефакт.

## Backbone sources

- Pro Git Book: [First-Time Git Setup](https://git-scm.com/book/ms/v2/Getting-Started-First-Time-Git-Setup.html)
  - Пройти: настройка `user.name`, `user.email` и проверка через `git config --list`.
- Pro Git Book: [Recording Changes to the Repository](https://git-scm.com/book/id/v2/Git-Basics-Recording-Changes-to-the-Repository)
  - Пройти: `git status`, `git add`, `git commit -m`.
- GitHub Docs: [Hello World](https://docs.github.com/en/get-started/quickstart/hello-world)
  - Пройти шаги: `Create a repository`, `Create a branch`, `Make and commit changes`, `Open a pull request`.

## Практический шаг после чтения

1. Инициализируй репозиторий для foundation-практики.
2. Добавь `README.md` и `scripts/hello_cli.py`.
3. Выполни commit с сообщением по смыслу изменения.
4. Запушь ветку и открой PR (или отправь ссылку на commit, если работаешь без PR).

## Что считаем done

- Есть видимый Git history с минимум одним осмысленным commit.
- Есть удалённая ссылка на commit/PR.
- В описании commit/PR понятно, какой учебный шаг закрыт.
