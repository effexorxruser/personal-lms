# SOURCE_REGISTRY

## Назначение

`content/sources/source_registry.yml` — это утвержденный каталог источников для content pipeline.

Реестр:

- фиксирует, какие источники разрешены для использования;
- задает retrieval-метаданные и usage-policy;
- служит опорой для валидации lesson `source_ids`.

Важно: реестр **не является fetcher-слоем** и сам ничего не скачивает.

## Что это не делает

- не выполняет web/MCP/network вызовы;
- не кэширует контент;
- не строит уроки автоматически.

Проверки `scripts/validate_content.py` и тесты работают локально по файлам репозитория.

## Формат source entry

Каждая запись в `source_registry.yml` должна содержать:

- `id` — стабильный slug идентификатор источника;
- `title` — человекочитаемое имя источника;
- `type` — роль источника в curated catalog;
- `language` — код языка источника (например `en`, `ru`, `en-us`);
- `allowed_usage` — допустимый тип использования в контенте;
- `canonical_url` — канонический URL источника;
- `retrieval` — блок retrieval-метаданных;
- `notes` — краткие пояснения по назначению источника;
- `usage_policy` (optional) — ограничения по пересказу/цитированию.

## Retrieval block

`retrieval` содержит:

- `mode` — предпочтительный retrieval-channel для будущего builder/fetcher;
- `priority` — приоритет источника при отборе;
- `direct_access` — допустим ли прямой доступ к источнику в retrieval-пайплайне;
- `preferred_sections` — список приоритетных URL разделов/страниц.

## Usage policy block

`usage_policy` (optional) содержит:

- `summarize_only` — использовать источник через summary-first подход;
- `quote_limit` — ограничение на объем прямого цитирования;
- `license` — опциональная заметка о license/usage условиях.

## Принятые enum значения

- `type`: `core` | `support`
- `allowed_usage`: `backbone` | `supplement`
- `retrieval.mode`: `web` | `mcp` | `manual` | `disabled`
- `retrieval.priority`: `high` | `medium` | `low`
- `usage_policy.quote_limit`: `none` | `short` | `moderate`

## Validation boundary

На этапе Source Registry Metadata Expansion v1:

- validation проверяет схему и ссылочную целостность (`lesson.source_ids` -> `source_registry.id`);
- validation/tests не выполняют сетевых запросов;
- runtime LMS, routes, UI, Lain, terminal и DB schema не затрагиваются.

## Follow-up

Следующий этап: **Source Fetch/Cache Builder v1** (отдельная задача).
