# Build Module Draft Prompt

You are generating a module draft for personal-lms.

## Context

- Block: `1`
- Module slug: `block-1-python-core`
- Blueprint title: `Python Foundation и developer workflow`
- Expected artifact: `CLI-утилиты на Python с базовой обработкой ошибок`
- Required source ids: `python-mooc, automate-boring-stuff, python-docs`
- Expected tasks: `foundation-python-types-and-flow, foundation-functions-and-modules, foundation-files-and-errors`
- Checkpoint slug: `block-1-python-core-checkpoint`

## Rules

- Russian-first learner text.
- Keep technical terms in English with short RU explanation.
- Do not ask learner to manually hunt random external sources.
- Sources are backbone context, not manual chores.
- Hyperlinks only as optional deep-dive.
- Keep execution-first: every lesson must have a concrete action.
- Do not invent source ids.
- Do not change course/module structure unless explicitly requested.
- Avoid motivational filler and vague advice.

## Output contract (`module.yml`)

Return YAML only with fields:

- `slug`
- `title`
- `description`
- `block`
- `objectives` (list)
- `lessons` (list of lesson keys)
- `checkpoint`

`checkpoint` must be `block-1-python-core-checkpoint`.
