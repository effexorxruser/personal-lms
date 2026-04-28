# Build Lesson Draft Prompt

You are generating a lesson draft for personal-lms.

## Context

- Block: `{{BLOCK_NUMBER}}`
- Module slug: `{{MODULE_SLUG}}`
- Lesson key target: `{{LESSON_KEY_HINT}}`
- Allowed source ids: `{{ALLOWED_SOURCE_IDS}}`
- Suggested source ids for this module: `{{REQUIRED_SOURCE_IDS}}`
- Suggested task slug: `{{TASK_SLUG_HINT}}`

## Rules

- Russian-first lesson text.
- Include Technical English terms with short Russian explanations.
- Treat lesson as standalone knowledge unit inside LMS.
- Do not instruct learner to "go read random links and come back".
- `What to read (EN source)` is optional deep-dive and source trace only.
- Lesson must be practical, runnable, and self-sufficient.
- Include one clear action and concrete completion criteria.
- Do not invent source ids.
- Do not modify course structure.
- Keep examples module-level appropriate; avoid advanced out-of-scope topics.
- Avoid vague motivational filler and fake citations.
- Use micro-step pedagogy: tiny example -> explanation -> slightly larger example -> task bridge.
- For early modules, first runnable example must be minimal and low-cognitive-load.
- For early modules, do not use type hints in the first explanation example.
- Introduce try/except, return, module import, and __main__ only after simpler steps.
- Markdown code fences must be valid: opening fence with language marker on own line, code starts next line, closing fence on own line.

## Output contract (`lesson.md`)

Return one markdown file with front matter:

---
key: ...
title: ...
summary: ...
objectives:
  - ...
checklist:
  - ...
task_slug: ...
source_ids:
  - ...
---

Body must include exactly these required sections:

- `## Why this matters (RU)`
- `## What to read (EN source)`
- `## What to skip`
- `## Action`
- `## Definition of Done`
- `## Technical English`

Body must ALSO include these knowledge-base sections:

- `## Core idea (RU)` with full explanation, not 2-line outline.
- `## Runnable example` with short executable code (where applicable).
- `## Run and expected output` with command and expected behavior (where applicable).
- `## Частые ошибки` (beginner mistakes).
- `## Как это связано с задачей` (practice bridge before/around Action).
- `## Optional media` OR explicit note `No media needed`.

Important:

- Do not make external reading mandatory for completion.
- Optional links may exist only as deep-dive references.
