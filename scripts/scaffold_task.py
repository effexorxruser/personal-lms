#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from app.content_scaffold import scaffold_task
from app.content_pipeline import TASK_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description="Создать task definition файл.")
    parser.add_argument("--slug", required=True, help="Slug задачи")
    parser.add_argument("--title", required=True, help="Название задачи")
    parser.add_argument("--summary", required=True, help="Summary задачи")
    parser.add_argument("--instructions", required=True, help="Инструкции для выполнения")
    parser.add_argument("--submission-type", default="text", help="Тип submission")
    parser.add_argument("--review-mode", default="deterministic", help="Режим review")
    parser.add_argument("--with-terminal", action="store_true", help="Добавить базовый terminal block")
    parser.add_argument("--task-root", type=Path, default=TASK_ROOT, help="Путь к content/tasks")
    args = parser.parse_args()

    task_path = scaffold_task(
        slug=args.slug,
        title=args.title,
        summary=args.summary,
        instructions=args.instructions,
        submission_type=args.submission_type,
        review_mode=args.review_mode,
        with_terminal=args.with_terminal,
        task_root=args.task_root,
    )

    print("Создана задача:")
    print(f"- task: {task_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Ошибка: {exc}", file=sys.stderr)
        raise SystemExit(1)
