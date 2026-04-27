#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.content_pipeline import CHECKPOINT_ROOT, CONTENT_ROOT, SOURCE_ROOT, TASK_ROOT, validate_content


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверить контентный graph перед запуском.")
    parser.add_argument("--content-root", type=Path, default=CONTENT_ROOT, help="Путь к content/courses")
    parser.add_argument("--task-root", type=Path, default=TASK_ROOT, help="Путь к content/tasks")
    parser.add_argument("--checkpoint-root", type=Path, default=CHECKPOINT_ROOT, help="Путь к content/checkpoints")
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT, help="Путь к content/sources")
    args = parser.parse_args()

    report = validate_content(
        content_root=args.content_root,
        task_root=args.task_root,
        checkpoint_root=args.checkpoint_root,
        source_root=args.source_root,
    )

    print("Content preflight")
    print("=================")
    print(f"Courses: {report.stats.courses}")
    print(f"Modules: {report.stats.modules}")
    print(f"Lessons: {report.stats.lessons}")
    print(f"Tasks: {report.stats.tasks}")
    print(f"Checkpoints: {report.stats.checkpoints}")

    if report.ok:
        print("\nOK: ошибок не найдено.")
        return 0

    print(f"\nНайдено ошибок: {len(report.errors)}")
    for index, issue in enumerate(report.errors, start=1):
        print(f"{index}. {issue.location}")
        print(f"   - {issue.message}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
