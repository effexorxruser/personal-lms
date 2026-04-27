#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.content_scaffold import scaffold_lesson
from app.content_pipeline import CONTENT_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description="Создать lesson markdown и добавить его в module.yml.")
    parser.add_argument("--course-slug", required=True, help="Slug курса")
    parser.add_argument("--module-slug", required=True, help="Slug модуля")
    parser.add_argument("--key", required=True, help="Key урока")
    parser.add_argument("--title", required=True, help="Название урока")
    parser.add_argument("--summary", required=True, help="Summary урока")
    parser.add_argument("--task-slug", default=None, help="Task slug (опционально)")
    parser.add_argument("--content-root", type=Path, default=CONTENT_ROOT, help="Путь к content/courses")
    args = parser.parse_args()

    lesson_path = scaffold_lesson(
        course_slug=args.course_slug,
        module_slug=args.module_slug,
        key=args.key,
        title=args.title,
        summary=args.summary,
        task_slug=args.task_slug,
        content_root=args.content_root,
    )

    print("Создан урок:")
    print(f"- lesson: {lesson_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Ошибка: {exc}", file=sys.stderr)
        raise SystemExit(1)
