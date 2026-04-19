from __future__ import annotations

from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO_ROOT, check=True, text=True, capture_output=True)


def test_scaffold_scripts_create_valid_skeleton(tmp_path: Path) -> None:
    content_root = tmp_path / "courses"
    task_root = tmp_path / "tasks"
    checkpoint_root = tmp_path / "checkpoints"

    _run(
        [
            sys.executable,
            "scripts/scaffold_course.py",
            "--slug",
            "demo-platform",
            "--title",
            "Demo Platform",
            "--description",
            "Курс для проверки scaffold.",
            "--starter-module-slug",
            "foundation",
            "--starter-lesson-key",
            "foundation-intro",
            "--content-root",
            str(content_root),
        ]
    )

    _run(
        [
            sys.executable,
            "scripts/scaffold_task.py",
            "--slug",
            "inspect-structure",
            "--title",
            "Проверить структуру",
            "--summary",
            "Найти ключевые слои.",
            "--instructions",
            "Найди router и loader.",
            "--with-terminal",
            "--task-root",
            str(task_root),
        ]
    )

    _run(
        [
            sys.executable,
            "scripts/scaffold_lesson.py",
            "--course-slug",
            "demo-platform",
            "--module-slug",
            "foundation",
            "--key",
            "backend-layout",
            "--title",
            "Урок 2: Layout",
            "--summary",
            "Проверить связность слоев.",
            "--task-slug",
            "inspect-structure",
            "--content-root",
            str(content_root),
        ]
    )

    _run(
        [
            sys.executable,
            "scripts/scaffold_module.py",
            "--course-slug",
            "demo-platform",
            "--slug",
            "api-basics",
            "--title",
            "API Basics",
            "--description",
            "Основы API.",
            "--first-lesson-key",
            "api-intro",
            "--first-lesson-title",
            "Урок 3: API старт",
            "--first-lesson-summary",
            "Первый урок по API.",
            "--content-root",
            str(content_root),
        ]
    )

    _run(
        [
            sys.executable,
            "scripts/scaffold_checkpoint.py",
            "--slug",
            "foundation-checkpoint",
            "--module-slug",
            "foundation",
            "--title",
            "Foundation Checkpoint",
            "--summary",
            "Промежуточный артефакт.",
            "--description",
            "Собери минимальный проверяемый артефакт.",
            "--checkpoint-root",
            str(checkpoint_root),
        ]
    )

    result = _run(
        [
            sys.executable,
            "scripts/validate_content.py",
            "--content-root",
            str(content_root),
            "--task-root",
            str(task_root),
            "--checkpoint-root",
            str(checkpoint_root),
        ]
    )

    assert "OK: ошибок не найдено" in result.stdout
