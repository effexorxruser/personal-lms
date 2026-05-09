#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.course_pack_preview_service import preview_course_pack


def main() -> int:
    parser = argparse.ArgumentParser(description="Краткое summary course pack для ручного review.")
    parser.add_argument("--pack-root", type=Path, required=True)
    args = parser.parse_args()
    pack_root = args.pack_root.resolve()
    report = preview_course_pack(pack_root)

    print("Course pack review summary")
    print("==========================")
    print(f"Путь: {pack_root}")
    print(f"Курсы: {', '.join(report.detected_courses) or '—'}")
    print(f"Модули/уроки: {report.detected_modules} / {report.detected_lessons}")
    print(f"Совместимость (без ERROR): {'да' if report.compatible else 'нет'}")
    print("")
    if report.errors:
        print("Первые ошибки:")
        for issue in report.errors[:8]:
            print(f"  - {issue.location}: {issue.message}")
        if len(report.errors) > 8:
            print(f"  ... и ещё {len(report.errors) - 8}")
    else:
        print("Ошибок уровня ERROR в отчёте нет.")
    print("")
    print("См. docs/course_authoring/COURSE_PACK_REVIEW_GUIDE.md для чеклиста ручного review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
