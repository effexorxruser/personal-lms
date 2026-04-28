# Build Module Draft Prompt

You are generating a module draft for personal-lms.

## Context

- Block: `{{BLOCK_NUMBER}}`
- Module slug: `{{MODULE_SLUG}}`
- Blueprint title: `{{BLOCK_TITLE}}`
- Expected artifact: `{{EXPECTED_ARTIFACT}}`
- Required source ids: `{{REQUIRED_SOURCE_IDS}}`
- Expected tasks: `{{EXPECTED_TASKS}}`
- Checkpoint slug: `{{CHECKPOINT_SLUG}}`

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

`checkpoint` must be `{{CHECKPOINT_SLUG}}`.
