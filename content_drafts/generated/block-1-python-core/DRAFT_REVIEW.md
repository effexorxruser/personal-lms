# Draft Review — block-1-python-core

## 1. Executive verdict

Draft quality is close to import-ready, but not publish-as-is.

- Structural schema compatibility for draft files is now OK (manual validation against `LessonFrontMatterSchema`, `TaskSchema`, `CheckpointSchema`).
- Blueprint alignment is mostly good.
- Main decision point: extra task `foundation-small-cli-utility` should not be imported as required task in first Block 1 publish pass.

Recommended outcome: **publish after edits**.

## 2. Blueprint alignment

Target blueprint:

- block: `1`
- module: `block-1-python-core`
- expected tasks:
  - `foundation-python-types-and-flow`
  - `foundation-functions-and-modules`
  - `foundation-files-and-errors`
- expected artifact: `CLI-утилиты на Python с базовой обработкой ошибок`

Alignment:

- Module slug/block/checkpoint: **aligned**
- Required source ids (`python-mooc`, `automate-boring-stuff`, `python-docs`): **aligned**
- Lessons count 4 (range 4-6): **aligned**
- Expected tasks: **all 3 present**
- Extra task `foundation-small-cli-utility`: **outside strict blueprint expected_tasks**

Extra task decision:

- **Decision (fixed):** keep `foundation-small-cli-utility` in draft as optional/stretch artifact, but do **not** import it as mandatory task in first publish pass.
- `04-small-cli-utility` is retained as checkpoint-prep lesson (no mandatory task import in first pass).
- Rationale: reduces scope and keeps first publish exactly aligned with blueprint contract.

## 3. Lesson review table

| Lesson | Verdict | Required edits | Risk |
|---|---|---|---|
| `01-python-values-and-control-flow` | accept | Optional: tighten wording in Action to mention exact input error cases (empty, text, out-of-range). | low |
| `02-functions-and-modules` | accept | Optional: add one explicit note about file layout (`same directory`) for beginners. | low |
| `03-files-errors-and-debugging` | edit | Keep focus on practical debugging only; remove any ambiguity about “тест-кейс” by stating it can be manual CLI check. | low |
| `04-small-cli-utility` | accept | Updated: lesson marked as checkpoint-prep and not tied to mandatory task import in first pass. | low |

Section heading check:

- All lessons contain required headings from validator:
  - `Why this matters (RU)`
  - `What to read (EN source)`
  - `What to skip`
  - `Action`
  - `Definition of Done`
  - `Technical English`

## 4. Task review table

| Task | Verdict | Required edits | Risk |
|---|---|---|---|
| `foundation-python-types-and-flow` | accept | None required. | low |
| `foundation-functions-and-modules` | accept | None required after YAML scalar fix. | low |
| `foundation-files-and-errors` | accept | None required after YAML scalar fix. | low |
| `foundation-small-cli-utility` | accept | Policy fixed: optional/stretch draft task, excluded from mandatory first publish import. | low |

Task design notes:

- `submission_type` values are supported (`command_output`).
- `review_mode` values are supported (`deterministic`).
- `definition_of_done` is concrete and reviewable.
- `terminal` block in extra task is schema-compatible and supported by current LMS task model.

## 5. Checkpoint review

Checkpoint is directionally strong and aligned with expected artifact (small Python CLI utilities + error handling).

Strengths:

- clear artifact orientation;
- concrete deliverables and evaluation criteria;
- realistic module-level integration.

Risk:

- previous wording “2-3 CLI utilities” was heavy for first Block 1 publish pass.

Applied edit:

- baseline reduced to “1 mandatory utility + optional second stretch utility”.

## 6. Source trace review

Result: **pass**.

- only valid source ids are used: `python-mooc`, `automate-boring-stuff`, `python-docs`;
- canonical URLs match `source_registry.yml`;
- preferred sections are consistent with registry metadata;
- explicitly states cache manifest was unavailable;
- no fake source ids and no fake citations detected.

## 7. Required edits before import

Required:

1. Policy fixed for `foundation-small-cli-utility`: optional/stretch only, not mandatory first import.
2. Lesson 4 coupling updated: checkpoint-prep, no mandatory task import in first pass.
3. Checkpoint baseline reduced (`2-3` -> `1+ optional`) for first publish safety.

Already fixed during review (minor structural defects):

- YAML scalars with backticks in task `definition_of_done` were normalized.
- YAML hint scalar with colon (`parse_values(...)`) was quoted.

## 8. Import plan

Planned target locations (future task, not executed here):

- `content/courses/python-backend-ai-foundation/modules/block-1-python-core/`
- `content/tasks/`
- `content/checkpoints/`

Proposed import sequence:

1. Finalize draft edits above.
2. Create module folder under active course and copy:
   - `module.yml`
   - `lessons/*.md`
3. Copy selected task files into `content/tasks/`:
   - required 3 blueprint tasks in first pass;
   - keep `foundation-small-cli-utility` in draft (or import later as optional by explicit decision).
4. Copy checkpoint into `content/checkpoints/`.
5. Update active course `course.yml`:
   - append `block-1-python-core` to module list after Block 0 modules.
6. Run integrity checks:
   - module lesson order, task references, checkpoint linkage.
7. Runtime behavior verification:
   - lesson next/prev inside same course;
   - unlock/progress transitions;
   - recap behavior with added module lessons.

## 9. Progress / migration risk

Adding Block 1 to active course will change progress denominator:

- users currently at 100% for Block 0-only course will likely become <100% after publish;
- this is expected but should be communicated as course expansion;
- no direct DB schema migration required;
- recommend release note: “active course expanded with Block 1 module”.

Optional mitigation:

- bump course version and include migration note in release docs/changelog.

## 10. Decision

**Final decision: publish after edits**

Reason:

- draft is structurally solid and instructionally good;
- only limited scope/pacing decisions remain (mainly extra task policy + checkpoint load tuning);
- no need to regenerate from scratch.
