# Block 1 Import Note

## What changed

Active course `python-backend-ai-foundation` was expanded from Block 0-only to Block 0 + Block 1 by importing module `block-1-python-core`.

## Imported content

- Module:
  - `content/courses/python-backend-ai-foundation/modules/block-1-python-core/module.yml`
- Lessons:
  - `01-python-values-and-control-flow.md`
  - `02-functions-and-modules.md`
  - `03-files-errors-and-debugging.md`
  - `04-small-cli-utility.md`
- Tasks (required set only):
  - `foundation-python-types-and-flow.yml`
  - `foundation-functions-and-modules.yml`
  - `foundation-files-and-errors.yml`
- Checkpoint:
  - `content/checkpoints/block-1-python-core-checkpoint.yml`

## Not imported yet

- Optional/stretch task remains draft-only:
  - `content_drafts/generated/block-1-python-core/tasks/foundation-small-cli-utility.yml`

This task is not published as mandatory content in the first Block 1 import pass.

## Progress impact

After adding Block 1, active course progress denominator increases.
Users who previously had 100% on Block 0-only route may now see course progress below 100%.

## Migration note

- No DB migration was applied.
- This progress shift is expected behavior for active course expansion.
- `foundation-real` draft course remains separate and is not merged into active route.

## Validation

- `python scripts/validate_content.py` -> pass
- `python -m pytest` -> pass
- `python -m ruff check .` -> pass
