# Build Checkpoint Draft Prompt

You are generating a checkpoint draft for personal-lms.

## Context

- Block: `{{BLOCK_NUMBER}}`
- Module slug: `{{MODULE_SLUG}}`
- Checkpoint slug target: `{{CHECKPOINT_SLUG}}`
- Expected artifact: `{{EXPECTED_ARTIFACT}}`

## Rules

- Russian-first learner-facing text.
- Checkpoint must integrate practical skills from module lessons.
- Keep scope realistic and MVP-friendly.
- No runtime/UI/platform changes.
- Avoid vague filler.

## Output contract (`checkpoint.yml`)

Return YAML only and follow CheckpointSchema fields:

- `slug`
- `title`
- `summary`
- `module_slug`
- `description`
- `project_description`
- `requirements`
- `deliverables`
- `evaluation_criteria`
- `definition_of_done`
- `submission_type` (`text` | `link` | `repository_link` | `command_output`)
- `portfolio_expectations`
- `hints`

`module_slug` must be `{{MODULE_SLUG}}`.
