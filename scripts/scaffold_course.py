#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from app.content_scaffold import scaffold_course
from app.content_pipeline import CONTENT_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description="Создать каркас нового курса.")
    parser.add_argument("--slug", required=True, help="Slug курса (lower-kebab-case)")
    parser.add_argument("--title", required=True, help="Название курса")
    parser.add_argument("--description", required=True, help="Краткое описание курса")
    parser.add_argument("--version", default="0.1.0", help="Версия курса")
    parser.add_argument("--estimated-weeks", type=int, default=8, help="Оценка длительности в неделях")
    parser.add_argument("--starter-module-slug", default="foundation", help="Slug стартового модуля")
    parser.add_argument("--starter-lesson-key", default="intro", help="Key стартового урока")
    parser.add_argument("--content-root", type=Path, default=CONTENT_ROOT, help="Путь к content/courses")
    args = parser.parse_args()

    created = scaffold_course(
        slug=args.slug,
        title=args.title,
        description=args.description,
        version=args.version,
        estimated_weeks=args.estimated_weeks,
        starter_module_slug=args.starter_module_slug,
        starter_lesson_key=args.starter_lesson_key,
        content_root=args.content_root,
    )

    print("Создан каркас курса:")
    for label, path in created.items():
        print(f"- {label}: {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Ошибка: {exc}", file=sys.stderr)
        raise SystemExit(1)
