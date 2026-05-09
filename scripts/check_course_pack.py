#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.content_pipeline import CHECKPOINT_ROOT, CONTENT_ROOT, SOURCE_ROOT, TASK_ROOT, ContentValidationIssue
from app.services.course_pack_preview_service import preview_course_pack


def _sort_issues(items: list[ContentValidationIssue]) -> list[ContentValidationIssue]:
    return sorted(items, key=lambda item: (item.location, item.message))


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверка переносимого course pack (граф + manifest + конфликты с target).")
    parser.add_argument("--pack-root", type=Path, required=True, help="Корень пака (внутри должен быть courses/)")
    parser.add_argument(
        "--target-content-root",
        type=Path,
        default=None,
        help="Каталог courses для проверки конфликтов (по умолчанию content/courses репозитория)",
    )
    parser.add_argument("--target-task-root", type=Path, default=None, help="По умолчанию content/tasks")
    parser.add_argument("--target-checkpoint-root", type=Path, default=None, help="По умолчанию content/checkpoints")
    parser.add_argument("--target-source-root", type=Path, default=None, help="По умолчанию content/sources")
    args = parser.parse_args()

    pack_root = args.pack_root.resolve()
    report = preview_course_pack(
        pack_root,
        target_content_root=args.target_content_root,
        target_task_root=args.target_task_root,
        target_checkpoint_root=args.target_checkpoint_root,
        target_source_root=args.target_source_root,
    )

    print("Course pack preflight")
    print("=====================")
    print(f"Pack: {pack_root}")
    print(f"Manifest: {'да' if report.manifest_present else 'нет'}")
    print(f"Courses (graph): {len(report.detected_courses)}")
    print(f"Modules: {report.detected_modules}")
    print(f"Lessons: {report.detected_lessons}")
    print(f"Tasks: {report.detected_tasks}")
    print(f"Checkpoints: {report.detected_checkpoints}")
    print("")

    if report.compatible:
        print("[OK] pack compatible (нет блокирующих ошибок)")

    for issue in _sort_issues(report.warnings):
        print(f"[WARN] {issue.location} — {issue.message}")

    for issue in _sort_issues(report.errors):
        print(f"[ERROR] {issue.location} — {issue.message}")

    print("")
    print(f"Summary: warnings={len(report.warnings)}, errors={len(report.errors)}")
    default_note = (
        f"(target по умолчанию: content={CONTENT_ROOT}, tasks={TASK_ROOT}, "
        f"checkpoints={CHECKPOINT_ROOT}, sources={SOURCE_ROOT})"
    )
    if (
        args.target_content_root is None
        and args.target_task_root is None
        and args.target_checkpoint_root is None
        and args.target_source_root is None
    ):
        print(default_note)

    return 0 if report.compatible else 1


if __name__ == "__main__":
    raise SystemExit(main())
