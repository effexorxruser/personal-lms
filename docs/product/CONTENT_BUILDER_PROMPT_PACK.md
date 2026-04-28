# Content Builder Prompt Pack

## Purpose

Content Builder Prompt Pack v1 подготавливает структурированный authoring input для Cursor/Codex/ChatGPT, чтобы генерировать draft-контент по source-backed модели без прямых network/API вызовов.

## What this does

- собирает context из:
  - `content/blueprints/backend_developer_6_months.yml`;
  - `content/sources/source_registry.yml`;
  - optional `var/source_cache/manifest.yml`;
- подготавливает prompt templates для:
  - module draft;
  - lesson draft;
  - task draft;
  - checkpoint draft;
  - draft validation;
- добавляет rules и output contract в единый prompt pack;
- сохраняет pack в `content_drafts/prompt_packs/...`.

## What this does not do

- не делает OpenAI/API вызовы;
- не делает web/MCP/fetch вызовы;
- не генерирует контент автоматически;
- не меняет runtime LMS;
- не меняет active course content.

## Files

- `content_builder/prompts/*.md` — prompt templates;
- `content_builder/rules/*.md` — authoring constraints;
- `content_builder/schemas/*.yml` — contracts;
- `scripts/build_content_prompt_pack.py` — CLI builder.

## CLI usage

- Build pack for one module:
  - `.venv/bin/python scripts/build_content_prompt_pack.py --block 1 --module block-1-python-core`
- Optional explicit output root:
  - `.venv/bin/python scripts/build_content_prompt_pack.py --block 1 --module block-1-python-core --output-root content_drafts`

## Output

CLI создает директорию:

- `content_drafts/prompt_packs/block-<N>-<module>-<timestamp>/`

Содержимое:

- `prompt_pack.yml` (input/output contract + paths);
- `prompts/` (готовые prompt files);
- `rules/` (authoring policy);
- `schemas/` (draft output contract + prompt pack schema).

## Authoring flow

1. Optional fetch/cache sources:
   - `.venv/bin/python scripts/fetch_source.py --source-id python-docs`
2. Build prompt pack:
   - `.venv/bin/python scripts/build_content_prompt_pack.py --block 1 --module block-1-python-core`
3. Copy pack into Cursor/Codex/ChatGPT and generate drafts.
4. Store generated drafts under `content_drafts/`.
5. Human review.
6. Only after review, copy approved files into `content/`.

## Testing policy

- Tests for prompt pack are local-only.
- No OpenAI/API/network calls in tests.
- Validation uses local repository files only.
