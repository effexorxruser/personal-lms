#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from app.content_scaffold import scaffold_checkpoint
from app.content_pipeline import CHECKPOINT_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description="Создать checkpoint definition файл.")
    parser.add_argument("--slug", required=True, help="Slug checkpoint")
    parser.add_argument("--module-slug", required=True, help="Slug модуля, к которому относится checkpoint")
    parser.add_argument("--title", required=True, help="Название checkpoint")
    parser.add_argument("--summary", required=True, help="Summary checkpoint")
    parser.add_argument("--description", required=True, help="Описание checkpoint")
    parser.add_argument("--submission-type", default="repository_link", help="Тип submission")
    parser.add_argument("--checkpoint-root", type=Path, default=CHECKPOINT_ROOT, help="Путь к content/checkpoints")
    args = parser.parse_args()

    checkpoint_path = scaffold_checkpoint(
        slug=args.slug,
        module_slug=args.module_slug,
        title=args.title,
        summary=args.summary,
        description=args.description,
        submission_type=args.submission_type,
        checkpoint_root=args.checkpoint_root,
    )

    print("Создан checkpoint:")
    print(f"- checkpoint: {checkpoint_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Ошибка: {exc}", file=sys.stderr)
        raise SystemExit(1)
