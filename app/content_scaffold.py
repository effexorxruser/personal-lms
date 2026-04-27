from __future__ import annotations

from pathlib import Path
import re

import yaml

from app.content_pipeline import CHECKPOINT_ROOT, CONTENT_ROOT, TASK_ROOT


def normalize_slug(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"[\s_]+", "-", normalized)
    normalized = re.sub(r"[^a-z0-9-]", "", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    if not normalized:
        raise ValueError("slug не может быть пустым")
    return normalized


def normalize_key(value: str) -> str:
    return normalize_slug(value)


def _write_yaml(path: Path, payload: dict) -> None:
    text = yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)
    path.write_text(text, encoding="utf-8")


def _read_yaml(path: Path) -> dict:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Ожидался YAML-объект в {path}")
    return raw


def _ensure_absent(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Уже существует: {path}")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _append_unique(items: list[str], value: str) -> list[str]:
    if value in items:
        return items
    return [*items, value]


def scaffold_course(
    *,
    slug: str,
    title: str,
    description: str,
    version: str = "0.1.0",
    estimated_weeks: int = 8,
    content_root: Path = CONTENT_ROOT,
    starter_module_slug: str = "foundation",
    starter_lesson_key: str = "intro",
) -> dict[str, Path]:
    course_slug = normalize_slug(slug)
    module_slug = normalize_slug(starter_module_slug)
    lesson_key = normalize_key(starter_lesson_key)

    course_dir = content_root / course_slug
    course_manifest = course_dir / "course.yml"
    modules_dir = course_dir / "modules"

    _ensure_absent(course_manifest)
    modules_dir.mkdir(parents=True, exist_ok=True)

    module_list = [module_slug]
    _write_yaml(
        course_manifest,
        {
            "slug": course_slug,
            "title": title.strip() or "Новый курс",
            "description": description.strip() or "Краткое описание курса.",
            "version": version.strip() or "0.1.0",
            "estimated_weeks": int(estimated_weeks),
            "modules": module_list,
        },
    )

    created: dict[str, Path] = {"course": course_manifest}
    module_result = scaffold_module(
        course_slug=course_slug,
        slug=module_slug,
        title="Модуль 1: Введение",
        description="Стартовый модуль для первого прохода.",
        first_lesson_key=lesson_key,
        first_lesson_title="Урок 1: Старт",
        first_lesson_summary="Короткий стартовый урок для проверки пайплайна.",
        content_root=content_root,
    )
    created.update({f"starter_{key}": value for key, value in module_result.items()})

    return created


def scaffold_module(
    *,
    course_slug: str,
    slug: str,
    title: str,
    description: str,
    first_lesson_key: str,
    first_lesson_title: str,
    first_lesson_summary: str,
    content_root: Path = CONTENT_ROOT,
) -> dict[str, Path]:
    normalized_course_slug = normalize_slug(course_slug)
    module_slug = normalize_slug(slug)
    lesson_key = normalize_key(first_lesson_key)

    course_dir = content_root / normalized_course_slug
    course_manifest = course_dir / "course.yml"
    if not course_manifest.exists():
        raise FileNotFoundError(f"Курс не найден: {course_manifest}")

    module_dir = course_dir / "modules" / module_slug
    module_manifest = module_dir / "module.yml"
    lesson_path = module_dir / "lessons" / f"{lesson_key}.md"

    _ensure_absent(module_manifest)
    _ensure_absent(lesson_path)

    lesson_path.parent.mkdir(parents=True, exist_ok=True)

    practice_lesson_key = f"{lesson_key}-practice"
    _write_yaml(
        module_manifest,
        {
            "slug": module_slug,
            "title": title.strip() or "Новый модуль",
            "description": description.strip() or "Краткое описание модуля.",
            "block": 1,
            "objectives": [
                "Сформировать минимальный учебный ритм по модулю.",
                "Подготовить артефакт для checkpoint.",
            ],
            "lessons": [lesson_key, practice_lesson_key],
            "checkpoint": "foundation-checkpoint",
        },
    )

    lesson_content = (
        "---\n"
        f"key: {lesson_key}\n"
        f"title: \"{(first_lesson_title.strip() or 'Новый урок')}\"\n"
        f"summary: {(first_lesson_summary.strip() or 'Кратко опиши цель урока.')}\n"
        "objectives:\n"
        "  - Зафиксировать цель урока\n"
        "  - Выполнить первый практический шаг\n"
        "checklist:\n"
        "  - Прочитать урок\n"
        "  - Подготовить задачу\n"
        "source_ids:\n"
        "  - python-docs\n"
        "---\n"
        "# Новый урок\n\n"
        "## Why this matters (RU)\n"
        "Коротко опиши, зачем нужен этот шаг в контексте модуля.\n\n"
        "## What to read (EN source)\n"
        "- Python Docs: https://docs.python.org/3/\n\n"
        "## What to skip\n"
        "Пропусти детали, которые не нужны для текущего шага.\n\n"
        "## Action\n"
        "Сделай минимальный проверяемый шаг и зафиксируй результат.\n\n"
        "## Definition of Done\n"
        "- Есть проверяемый результат.\n"
        "- Результат можно воспроизвести.\n\n"
        "## Technical English\n"
        "- baseline\n"
        "- run\n"
        "- output\n"
    )
    lesson_path.write_text(lesson_content, encoding="utf-8")

    practice_lesson_path = module_dir / "lessons" / f"{practice_lesson_key}.md"
    practice_lesson_content = (
        "---\n"
        f"key: {practice_lesson_key}\n"
        f"title: \"{(first_lesson_title.strip() or 'Новый урок')} · Практика\"\n"
        "summary: Практический follow-up для закрепления шага.\n"
        "objectives:\n"
        "  - Закрепить базовый сценарий\n"
        "  - Проверить воспроизводимость результата\n"
        "checklist:\n"
        "  - Повторить шаги\n"
        "  - Зафиксировать наблюдения\n"
        "source_ids:\n"
        "  - python-docs\n"
        "---\n"
        "# Практика\n\n"
        "## Why this matters (RU)\n"
        "Практика закрепляет результат первого шага.\n\n"
        "## What to read (EN source)\n"
        "- Python Docs: https://docs.python.org/3/\n\n"
        "## What to skip\n"
        "Не углубляйся в расширенные темы на этом этапе.\n\n"
        "## Action\n"
        "Повтори сценарий и убедись, что он стабильно работает.\n\n"
        "## Definition of Done\n"
        "- Шаг повторён без расхождений.\n"
        "- Есть короткий run-log.\n\n"
        "## Technical English\n"
        "- repeatable\n"
        "- verification\n"
        "- checkpoint\n"
    )
    practice_lesson_path.write_text(practice_lesson_content, encoding="utf-8")

    course_payload = _read_yaml(course_manifest)
    modules = [normalize_slug(item) for item in course_payload.get("modules", [])]
    course_payload["modules"] = _append_unique(modules, module_slug)
    _write_yaml(course_manifest, course_payload)

    return {
        "module": module_manifest,
        "lesson": lesson_path,
        "practice_lesson": practice_lesson_path,
        "course": course_manifest,
    }


def scaffold_lesson(
    *,
    course_slug: str,
    module_slug: str,
    key: str,
    title: str,
    summary: str,
    content_root: Path = CONTENT_ROOT,
    task_slug: str | None = None,
) -> Path:
    normalized_course_slug = normalize_slug(course_slug)
    normalized_module_slug = normalize_slug(module_slug)
    lesson_key = normalize_key(key)
    normalized_task_slug = normalize_slug(task_slug) if task_slug else None

    module_dir = content_root / normalized_course_slug / "modules" / normalized_module_slug
    module_manifest = module_dir / "module.yml"
    if not module_manifest.exists():
        raise FileNotFoundError(f"Модуль не найден: {module_manifest}")

    lesson_path = module_dir / "lessons" / f"{lesson_key}.md"
    _ensure_absent(lesson_path)
    _ensure_parent(lesson_path)

    task_line = f"task_slug: {normalized_task_slug}\n" if normalized_task_slug else ""
    lesson_content = (
        "---\n"
        f"key: {lesson_key}\n"
        f"title: \"{(title.strip() or 'Новый урок')}\"\n"
        f"summary: {(summary.strip() or 'Краткое описание урока.')}\n"
        "objectives:\n"
        "  - Определи цель урока\n"
        "  - Выполни минимальный практический шаг\n"
        "checklist:\n"
        "  - Прочитать материалы\n"
        "  - Подготовить результат\n"
        "source_ids:\n"
        "  - python-docs\n"
        f"{task_line}"
        "---\n"
        "# Заголовок урока\n\n"
        "## Why this matters (RU)\n"
        "Опиши практический смысл этого урока.\n\n"
        "## What to read (EN source)\n"
        "- Python Docs: https://docs.python.org/3/\n\n"
        "## What to skip\n"
        "Не углубляйся в детали, не влияющие на текущий шаг.\n\n"
        "## Action\n"
        "Выполни минимальный практический шаг и зафиксируй результат.\n\n"
        "## Definition of Done\n"
        "- Есть проверяемый результат.\n"
        "- Результат можно воспроизвести.\n\n"
        "## Technical English\n"
        "- execution\n"
        "- input\n"
        "- output\n"
    )
    lesson_path.write_text(lesson_content, encoding="utf-8")

    module_payload = _read_yaml(module_manifest)
    lessons = [normalize_key(item) for item in module_payload.get("lessons", [])]
    module_payload["lessons"] = _append_unique(lessons, lesson_key)
    _write_yaml(module_manifest, module_payload)

    return lesson_path


def scaffold_task(
    *,
    slug: str,
    title: str,
    summary: str,
    instructions: str,
    task_root: Path = TASK_ROOT,
    submission_type: str = "text",
    review_mode: str = "deterministic",
    with_terminal: bool = False,
) -> Path:
    task_slug = normalize_slug(slug)
    path = task_root / f"{task_slug}.yml"
    _ensure_absent(path)
    _ensure_parent(path)

    payload: dict = {
        "slug": task_slug,
        "title": title.strip() or "Новая задача",
        "summary": summary.strip() or "Краткая цель задачи.",
        "instructions": instructions.strip() or "Опиши, что нужно сделать для прохождения шага.",
        "submission_type": submission_type,
        "definition_of_done": [
            "Есть проверяемый результат выполнения.",
            "Результат связан с текущим уроком.",
        ],
        "review_mode": review_mode,
        "hints": [
            "Начни с минимального шага.",
            "Проверь результат перед отправкой.",
        ],
    }

    if with_terminal:
        payload["terminal"] = {
            "enabled": True,
            "presets": [
                {"label": "Показать помощь", "command": "help"},
                {"label": "Показать задание", "command": "show task"},
            ],
            "allow_manual_input": True,
            "allowed_commands": ["help", "pwd", "tree", "python", "pytest", "show"],
        }

    _write_yaml(path, payload)
    return path


def scaffold_checkpoint(
    *,
    slug: str,
    module_slug: str,
    title: str,
    summary: str,
    description: str,
    checkpoint_root: Path = CHECKPOINT_ROOT,
    submission_type: str = "repository_link",
) -> Path:
    checkpoint_slug = normalize_slug(slug)
    normalized_module_slug = normalize_slug(module_slug)

    path = checkpoint_root / f"{checkpoint_slug}.yml"
    _ensure_absent(path)
    _ensure_parent(path)

    payload = {
        "slug": checkpoint_slug,
        "module_slug": normalized_module_slug,
        "title": title.strip() or "Новый checkpoint",
        "summary": summary.strip() or "Краткое описание checkpoint.",
        "description": description.strip() or "Опиши ожидаемый итоговый артефакт.",
        "project_description": "Короткое описание проекта и его границ для проверки.",
        "requirements": [
            "Есть проверяемый артефакт.",
            "Есть короткое описание результата.",
        ],
        "deliverables": [
            "Ссылка на артефакт или репозиторий.",
            "README с шагами запуска и проверки.",
        ],
        "evaluation_criteria": [
            "Артефакт воспроизводим по инструкции.",
            "Цели checkpoint достигнуты в рамках scope.",
        ],
        "definition_of_done": [
            "Результат можно проверить по ссылке или тексту.",
            "Артефакт соответствует целям модуля.",
        ],
        "submission_type": submission_type,
        "portfolio_expectations": [
            "Артефакт можно показать как часть портфолио.",
        ],
        "hints": [
            "Держи scope небольшим и проверяемым.",
        ],
    }

    _write_yaml(path, payload)
    return path
