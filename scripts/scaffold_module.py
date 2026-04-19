#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from app.content_scaffold import scaffold_module
from app.content_pipeline import CONTENT_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description="Создать модуль внутри существующего курса.")
    parser.add_argument("--course-slug", required=True, help="Slug курса")
    parser.add_argument("--slug", required=True, help="Slug модуля")
    parser.add_argument("--title", required=True, help="Название модуля")
    parser.add_argument("--description", required=True, help="Описание модуля")
    parser.add_argument("--first-lesson-key", required=True, help="Key первого урока")
    parser.add_argument("--first-lesson-title", required=True, help="Заголовок первого урока")
    parser.add_argument("--first-lesson-summary", required=True, help="Summary первого урока")
    parser.add_argument("--content-root", type=Path, default=CONTENT_ROOT, help="Путь к content/courses")
    args = parser.parse_args()

    created = scaffold_module(
        course_slug=args.course_slug,
        slug=args.slug,
        title=args.title,
        description=args.description,
        first_lesson_key=args.first_lesson_key,
        first_lesson_title=args.first_lesson_title,
        first_lesson_summary=args.first_lesson_summary,
        content_root=args.content_root,
    )

    print("Создан каркас модуля:")
    for label, path in created.items():
        print(f"- {label}: {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Ошибка: {exc}", file=sys.stderr)
        raise SystemExit(1)
