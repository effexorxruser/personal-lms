# Source Fetch/Cache

## Purpose

Source Fetch/Cache v1 добавляет контролируемый слой извлечения approved source-текстов из `source_registry` в локальный кэш для будущего content builder.

## What this does

- читает approved sources из `content/sources/source_registry.yml`;
- выбирает источник по `source_id` (или все источники через CLI);
- выполняет controlled fetch для `retrieval.mode: web`;
- сохраняет локальные snapshots в `var/source_cache`;
- пишет retrieval manifest (`manifest.yml`) с run-логом, статусами и метаданными.

## What this does not do

- не генерирует lessons/tasks/checkpoints;
- не строит LLM prompts;
- не меняет runtime LMS;
- не меняет routes, DB schema, UI, Lain, terminal;
- не меняет `content/courses/`, `content/tasks/`, `content/checkpoints/`.

## Cache location

Локальный кэш хранится в:

- `var/source_cache/manifest.yml`
- `var/source_cache/snapshots/<source_id>/<sha256>.txt`

Кэш локальный и не коммитится в git (`.gitignore` содержит `var/source_cache/`).

## Manifest format

`manifest.yml` хранит append-only список запусков:

- `run_id`
- `source_id`
- `url`
- `retrieval_mode`
- `status`
- `http_status`
- `content_hash`
- `snapshot_path`
- `fetched_at`
- `content_length`
- `error`

Статусы:

- `ok`
- `manual_required`
- `disabled`
- `unsupported_mode`
- `error`

## Retrieval modes

- `web`: HTTP GET с timeout, user-agent, max-bytes, записью snapshot + manifest.
- `mcp`: v1 не реализует MCP retrieval, возвращает `unsupported_mode`.
- `manual`: network fetch не выполняется, статус `manual_required`.
- `disabled`: retrieval отключен, статус `disabled`.

## CLI usage

Основные команды:

- `.venv/bin/python scripts/fetch_source.py --source-id python-docs`
- `.venv/bin/python scripts/fetch_source.py --source-id python-docs --section all`
- `.venv/bin/python scripts/fetch_source.py --all`

Где:

- `--section canonical` (default): fetch только `canonical_url`;
- `--section all`: fetch `canonical_url` и `preferred_sections`.

## Testing policy

- Тесты fetch/cache слоя не используют интернет.
- HTTP слой подменяется mock/stub в unit tests.
- Проверяется manifest/snapshot запись, controlled статусы и path safety.

## Future builder integration

Следующий этап — Source-backed Content Builder v1, который будет читать локальный кэш и manifest как входные данные.

Текущий fetch/cache слой не является content generator и не является runtime LMS feature.
