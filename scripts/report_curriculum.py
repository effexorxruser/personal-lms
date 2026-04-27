#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.content_pipeline import validate_content


def main() -> int:
    report = validate_content()

    print(f"Blocks: 7")
    print(f"Modules: {report.stats.modules}")
    print(f"Lessons: {report.stats.lessons}")
    print(f"Tasks: {report.stats.tasks}")
    print(f"Checkpoints: {report.stats.checkpoints}")

    print("Ошибки:")
    if report.ok:
        print("- нет")
        return 0

    for issue in report.errors:
        print(f"- {issue.location}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
