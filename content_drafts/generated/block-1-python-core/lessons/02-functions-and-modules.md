---
key: 02-functions-and-modules
title: Функции и модули для переиспользуемого кода
summary: Разделяем код на функции, переносим логику в модуль и проверяем повторное использование через импорт.
objectives:
  - Выделять повторяющуюся логику в функции.
  - Понимать параметры, возвращаемые значения и простые type hints.
  - Использовать модульный импорт в небольшом проекте.
checklist:
  - Вынес повторяющиеся части в отдельные функции.
  - Сделал импорт из своего модуля.
  - Проверил, что результат одинаков при повторных запусках.
task_slug: foundation-functions-and-modules
source_ids:
  - python-mooc
  - automate-boring-stuff
  - python-docs
---

## Why this matters (RU)
Backend-код быстро разрастается. Если не выделять функции и модули, каждый новый шаг увеличивает хаос и риск ошибок.  
Функции и модули дают базу для чистого, проверяемого кода.

## What to read (EN source)
- Python MOOC: functions, parameters, return values.
- Automate the Boring Stuff: chapters with reusable helper functions.
- Python docs tutorial: modules and packages (базовый уровень).

Опциональный deep dive:
- https://docs.python.org/3/tutorial/modules.html

## What to skip
- Полная теория packaging и публикация на PyPI.
- Сложные темы про import hooks и internals.

## Action
Сделай два файла:
- `text_utils.py`
- `run_text_utils.py`

В `text_utils.py` реализуй функции:
1. `word_count(text: str) -> int`
2. `char_count(text: str) -> int`
3. `normalize_spaces(text: str) -> str`

В `run_text_utils.py`:
- импортируй функции из `text_utils.py`;
- обработай строку из `input()`;
- выведи количество слов, символов и нормализованную строку.

## Definition of Done
- Логика вынесена в функции, а не написана целиком в одном файле.
- `run_text_utils.py` корректно использует `import`.
- Функции возвращают значения, а не только печатают их.
- На пустой строке скрипт не падает.

## Technical English
- **function** — функция, переиспользуемый блок кода.
- **parameter** — параметр, вход функции.
- **return value** — возвращаемое значение функции.
- **module** — модуль, Python-файл с кодом для импорта.
- **import** — подключение кода из другого модуля.
