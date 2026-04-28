# LESSON_AUTHORING_STANDARD

## 1. Core principle

Урок в LMS — самостоятельная учебная единица.

- learner должен понимать тему и выполнить шаг без обязательного web surfing;
- внешние источники используются как backbone для автора/AI;
- итоговый учебный материал должен быть упакован внутрь LMS lesson.

## 2. Required validator headings

Текущие обязательные headings (по `app/content_pipeline.py`) должны сохраняться в каждом уроке:

- `Why this matters (RU)`
- `What to read (EN source)`
- `What to skip`
- `Action`
- `Definition of Done`
- `Technical English`

## 3. Required knowledge-base sections

Каждый новый урок должен дополнительно включать:

- `Core idea (RU)` с цельным объяснением темы;
- runnable code example (where applicable);
- command + expected output (where applicable);
- `Частые ошибки`;
- `Как это связано с задачей`;
- `Optional media` или явное `No media needed`;
- практичный `Technical English` glossary.

## 4. External source policy

`What to read (EN source)` используется как:

- optional deep dive;
- source trace/reference;
- подтверждение backbone-источников.

`What to read (EN source)` не должен быть:

- главным учебным блоком;
- инструкцией “прочитай сайт и вернись”.

## 5. Code example policy

Примеры в уроке должны быть:

- короткими и runnable;
- соответствующими уровню текущего модуля;
- без тем, которые ещё не введены;
- с expected output, если пример предполагает запуск.

## 6. Media policy

YouTube/iframe/media:

- optional и не обязательны для completion;
- не добавлять случайные ссылки без review;
- если renderer/sanitizer не пропускает iframe, использовать structured placeholder.

## 7. Task bridge policy

Перед `Action` или непосредственно перед практической частью должно быть объяснение, как теория превращается в задачу:

- что уже изучено;
- какой шаг делается в задаче;
- какой результат ожидается.

## 8. Anti-patterns

Запрещено:

- skeletal outline lessons;
- “прочитай external docs” как основной путь обучения;
- fake citations;
- advanced topics вне текущего scope;
- слишком большие примеры;
- vague motivational filler без учебной ценности.

## 9. Markdown code fence rule

Для каждого code block:

- opening fence на отдельной строке с language marker (например ` ```python `);
- код начинается со следующей строки;
- closing fence на отдельной строке;
- не допускать “сломанных” блоков, где ` ```python ` попадает в обычный текст.

## 10. Beginner complexity rule

Для ранних модулей (Block 0 / Block 1):

- первый пример должен быть минимальным и понятным;
- не использовать type hints в первом объясняющем примере;
- не давать плотный multi-concept пример как первый runnable block;
- `try/except`, `return`, `module`, `if __name__ == "__main__"` вводить после простого шага.

## 11. Micro-step rule

Урок строится лестницей:

`tiny example -> explanation -> slightly larger example -> task bridge`.

Каждый следующий шаг должен опираться на предыдущий, без резких прыжков сложности.
