# COURSE GENERATION READINESS

## Назначение

Документ фиксирует readiness-gate перед генерацией curriculum-артефактов.
Цель: безопасно перейти от blueprint к block-by-block generation без расползания scope.

## Gate перед генерацией блока

Перед стартом генерации любого блока (0..6) должно быть выполнено:

1. **Blueprint completeness**
   - для блока заполнены `title`, `modules`, `lesson_count_range`, `required_source_ids`, `expected_tasks`, `checkpoint_slug`, `expected_artifact`;
   - у блока нет пустых module entries.
2. **Source readiness**
   - все `required_source_ids` блока существуют в `content/sources/source_registry.yml`;
   - источники соответствуют `docs/product/SOURCE_STACK.md`.
3. **Task/checkpoint readiness**
   - task/checkpoint slug-ы для блока либо уже существуют, либо явно отмечены как очередь на генерацию;
   - не создаются конфликтующие slug-ы.
4. **Validation clean state**
   - `python scripts/validate_content.py` проходит без ошибок;
   - integrity тесты проходят.
5. **Manual reviewer sign-off**
   - reviewer подтверждает, что блок не расширяет архитектуру и не ломает MVP guardrails.

## Gate перед генерацией полного курса

Полная генерация разрешается только если:

1. Все блоки 0..6 имеют заполненные modules и не имеют пустых блоков.
2. Source registry покрывает весь approved source stack.
3. Для каждого блока определен checkpoint artifact outcome.
4. Readiness документы актуальны:
   - `COURSE_GENERATION_READINESS.md`
   - `LAIN_CURRICULUM_READINESS.md`
   - `TERMINAL_READINESS.md`
5. `scripts/report_curriculum.py` показывает отсутствие missing source ids и empty blocks.
6. Пройден manual review checklist (ниже) и зафиксирован approve.

## Команды валидации

```bash
python scripts/validate_content.py
python scripts/report_curriculum.py
PYTHONPATH=. pytest tests/test_content_validation.py tests/test_content_integrity.py
```

## Manual review checklist

- [ ] Blueprint покрывает блоки 0..6 без пустых `modules`.
- [ ] У каждого модуля есть lesson range, expected tasks, checkpoint, artifact.
- [ ] Все source id из blueprint присутствуют в source registry.
- [ ] Source registry не содержит случайных источников вне SOURCE_STACK.
- [ ] Изменения не меняют runtime architecture.
- [ ] Изменения не ослабляют content validation.
- [ ] Нет попытки сгенерировать весь курс за один проход без block gate.

## Риски и blockers

### Риски

- **Scope creep в source registry**: добавление неутвержденных источников ухудшает consistency.
- **Pseudo-complete blueprint**: заполнены поля, но без проверяемых artifact outcomes.
- **Mass generation без block gate**: высокий риск структурного шума в контенте.

### Blockers

- Validation ошибки в content/tasks/checkpoints.
- Empty blocks в master blueprint.
- Missing source ids между blueprint и registry.
- Отсутствует reviewer sign-off на конкретный блок.
