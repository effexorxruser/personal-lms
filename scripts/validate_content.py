#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.content_pipeline import (
    CHECKPOINT_ROOT,
    CONTENT_ROOT,
    SOURCE_ROOT,
    TASK_ROOT,
    ContentValidationIssue,
    validate_content,
)


def _issue_under_course_slug(location: str, *, content_root: Path) -> str | None:
    try:
        rel = Path(location).resolve().relative_to(content_root.resolve())
    except ValueError:
        return None
    if rel.parts:
        return rel.parts[0]
    return None


def _sort_issues(items):
    return sorted(items, key=lambda item: (item.location, item.message))


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

    known_courses = sorted({p.resolve().parent.name for p in args.content_root.glob("*/course.yml")})
    course_errors: dict[str, list[ContentValidationIssue]] = {slug: [] for slug in known_courses}
    global_errors: list[ContentValidationIssue] = []

    for issue in report.errors:
        slug = _issue_under_course_slug(issue.location, content_root=args.content_root)
        if slug is not None and slug in course_errors:
            course_errors[slug].append(issue)
        else:
            global_errors.append(issue)

    print("Content preflight")
    print("=================")
    print(f"Courses: {report.stats.courses}")
    print(f"Modules: {report.stats.modules}")
    print(f"Lessons: {report.stats.lessons}")
    print(f"Tasks: {report.stats.tasks}")
    print(f"Checkpoints: {report.stats.checkpoints}")
    print("")

    for slug in sorted(known_courses):
        if not course_errors.get(slug):
            print(f"[OK] course {slug}")

    for issue in _sort_issues(report.warnings):
        print(f"[WARN] {issue.location} — {issue.message}")

    for issue in _sort_issues(global_errors):
        print(f"[ERROR] {issue.location} — {issue.message}")

    for slug in sorted(known_courses):
        for issue in _sort_issues(course_errors[slug]):
            print(f"[ERROR] {issue.location} — {issue.message}")

    print("")
    print(f"Summary: warnings={len(report.warnings)}, errors={len(report.errors)}")

    if report.ok:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
