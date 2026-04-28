# Build Task Draft Prompt

You are generating a task draft for personal-lms.

## Context

- Block: `{{BLOCK_NUMBER}}`
- Module slug: `{{MODULE_SLUG}}`
- Task slug target: `{{TASK_SLUG_HINT}}`
- Task must map to lesson action for this module.

## Rules

- Russian-first instruction style.
- Technical English terms are allowed with short RU explanation.
- Task must be execution-first and verifiable.
- No vague motivational filler.
- Do not invent source ids or module structure.

## Output contract (`task.yml`)

Return YAML only and follow TaskSchema fields:

- `slug`
- `title`
- `summary`
- `instructions`
- `submission_type` (`text` | `link` | `command_output`)
- `definition_of_done` (list, non-empty)
- `review_mode` (`deterministic` | `manual`)
- `hints` (list)
- `terminal` (optional, only when task needs terminal execution)

If `terminal` is used, include:

- `enabled`
- `presets`
- `allow_manual_input`
- `allowed_commands`
