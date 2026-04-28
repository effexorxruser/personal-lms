# Validate Draft Prompt

You are validating generated draft files before they are copied to `content/`.

## Scope

Review draft `module.yml`, `lesson.md`, `task.yml`, `checkpoint.yml` for:

- schema compliance;
- source id correctness;
- execution-first quality;
- Russian-first style;
- technical English support;
- clarity and non-vague actionability.

## Hard checks

- Lesson front matter includes `source_ids` from approved registry only.
- Lesson contains sections:
  - `Why this matters (RU)`
  - `What to read (EN source)`
  - `What to skip`
  - `Action`
  - `Definition of Done`
  - `Technical English`
- Lesson also contains knowledge-base sections:
  - `Core idea (RU)`
  - `Runnable example` (where applicable)
  - `Run and expected output` (where applicable)
  - `Частые ошибки`
  - `Как это связано с задачей`
  - `Optional media` or explicit `No media needed`
- Markdown fences in lesson code blocks are valid and renderable.
- For early-module lessons, first example is minimal and not overloaded.
- For early-module lessons, type hints are not used in the first explanation example.
- Task includes `definition_of_done` and valid `submission_type`.
- Checkpoint includes required fields (`project_description`, `deliverables`, `evaluation_criteria`, etc.).
- No instruction that forces manual source hunting.
- `What to read (EN source)` is optional deep dive, not primary lesson content.
- No unauthorized course structure changes.

## Output

Return:

1) `PASS` or `FAIL`
2) bullet list of exact violations
3) minimal patch suggestions per file
