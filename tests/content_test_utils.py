from __future__ import annotations

from pathlib import Path

import yaml


def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def write_lesson(path: Path, *, key: str, title: str, summary: str, task_slug: str | None = None, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    front_lines = [
        "---",
        f"key: {key}",
        f"title: \"{title}\"",
        f"summary: {summary}",
        "objectives:",
        "  - Зафиксировать цель",
        "checklist:",
        "  - Выполнить шаг",
    ]
    if task_slug:
        front_lines.append(f"task_slug: {task_slug}")
    front_lines.append("---")
    text = "\n".join(front_lines) + "\n" + body.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def create_valid_content_tree(base_dir: Path) -> dict[str, Path]:
    content_root = base_dir / "courses"
    task_root = base_dir / "tasks"
    checkpoint_root = base_dir / "checkpoints"

    course_slug = "demo-course"
    module_slug = "foundation"
    lesson_key = "demo-intro"
    task_slug = "demo-task"
    checkpoint_slug = "demo-checkpoint"

    course_dir = content_root / course_slug
    module_dir = course_dir / "modules" / module_slug

    write_yaml(
        course_dir / "course.yml",
        {
            "slug": course_slug,
            "title": "Demo Course",
            "description": "Демо курс для тестов.",
            "version": "0.1.0",
            "estimated_weeks": 4,
            "modules": [module_slug],
        },
    )

    write_yaml(
        module_dir / "module.yml",
        {
            "slug": module_slug,
            "title": "Foundation",
            "description": "Базовый модуль.",
            "lessons": [lesson_key],
        },
    )

    write_lesson(
        module_dir / "lessons" / f"{lesson_key}.md",
        key=lesson_key,
        title="Demo Intro",
        summary="Стартовый урок.",
        task_slug=task_slug,
        body="# Demo\n\nПрактика по шагам.",
    )

    write_yaml(
        task_root / f"{task_slug}.yml",
        {
            "slug": task_slug,
            "title": "Demo Task",
            "summary": "Короткая задача.",
            "instructions": "Сделай минимальный шаг.",
            "submission_type": "text",
            "definition_of_done": ["Есть результат."],
            "review_mode": "deterministic",
            "hints": ["Начни с малого."],
        },
    )

    write_yaml(
        checkpoint_root / f"{checkpoint_slug}.yml",
        {
            "slug": checkpoint_slug,
            "module_slug": module_slug,
            "title": "Demo Checkpoint",
            "summary": "Контрольная точка.",
            "description": "Покажи промежуточный артефакт.",
            "requirements": ["Есть артефакт."],
            "definition_of_done": ["Артефакт проверяем."],
            "submission_type": "repository_link",
            "portfolio_expectations": ["Можно показать в портфолио."],
            "hints": ["Не усложняй."],
        },
    )

    return {
        "content_root": content_root,
        "task_root": task_root,
        "checkpoint_root": checkpoint_root,
        "course_dir": course_dir,
        "module_dir": module_dir,
    }
