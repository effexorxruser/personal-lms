# Build Lesson Draft Prompt

You are generating a lesson draft for personal-lms.

## Context

- Block: `1`
- Module slug: `block-1-python-core`
- Lesson key target: `block-1-python-core-lesson-key`
- Allowed source ids: `automate-boring-stuff, fastapi-docs, git-docs, github-actions-docs, github-docs, github-skills, httpx-docs, mdn-http, openai-cookbook, openai-docs, pytest-docs, python-debugging-guides, python-docs, python-logging-docs, python-mooc, sqlbolt, sqlite-docs, terminal-reference, vscode-docs`
- Suggested source ids for this module: `python-mooc, automate-boring-stuff, python-docs`
- Suggested task slug: `foundation-python-types-and-flow`

## Rules

- Russian-first lesson text.
- Include Technical English terms with short Russian explanations.
- Do not instruct learner to "go read random links and come back".
- External links are optional deep-dive only.
- Lesson must be practical and runnable.
- Include one clear action and concrete completion criteria.
- Do not invent source ids.
- Do not modify course structure.

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
