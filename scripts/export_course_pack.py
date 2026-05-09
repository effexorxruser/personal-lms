#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.content_pipeline import (
    CHECKPOINT_ROOT,
    CONTENT_ROOT,
    SOURCE_ROOT,
    TASK_ROOT,
    ContentValidationException,
    load_content_bundle,
)
from app.course_pack.manifest import write_pack_manifest


def _tasks_referenced_by_courses(bundle, course_slugs: set[str], task_root: Path) -> dict[str, Path]:
    task_root_res = task_root.resolve()
    out: dict[str, Path] = {}
    for course in bundle.courses:
        if course.schema.slug not in course_slugs:
            continue
        for module in course.modules_by_folder.values():
            for lesson in module.lessons_by_file_stem.values():
                slug = lesson.schema.task_slug
                if not slug:
                    continue
                task = bundle.tasks_by_slug.get(slug)
                if task is None:
                    continue
                try:
                    task.path.resolve().relative_to(task_root_res)
                except ValueError:
                    continue
                out[slug] = task.path.resolve()
    return out


def _checkpoints_referenced_by_courses(
    bundle,
    course_slugs: set[str],
    checkpoint_root: Path,
) -> dict[str, Path]:
    cp_res = checkpoint_root.resolve()
    out: dict[str, Path] = {}
    for course in bundle.courses:
        if course.schema.slug not in course_slugs:
            continue
        for module in course.modules_by_folder.values():
            ck_slug = module.schema.checkpoint
            ck = bundle.checkpoints_by_slug.get(ck_slug)
            if ck is None:
                continue
            try:
                ck.path.resolve().relative_to(cp_res)
            except ValueError:
                continue
            out[ck_slug] = ck.path.resolve()
    return out


def _zip_pack(output_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output_dir.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(output_dir)
            archive.write(path, arcname=str(rel).replace("\\", "/"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Экспорт выбранных курсов в переносимый course pack.")
    parser.add_argument(
        "--course-slug",
        action="append",
        dest="course_slugs",
        metavar="SLUG",
        required=True,
        help="Slug курса (можно указать несколько раз).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Корень пака (например exports/my-pack). По умолчанию: exports/<первый-slug>-pack",
    )
    parser.add_argument("--include-sources", action="store_true", help="Скопировать sources/source_registry.yml")
    parser.add_argument(
        "--include-referenced-global-tasks",
        action="store_true",
        help="Скопировать только глобальные tasks, на которые ссылаются уроки выбранных курсов",
    )
    parser.add_argument(
        "--include-referenced-global-checkpoints",
        action="store_true",
        help="Скопировать только глобальные checkpoints из module.yml выбранных курсов",
    )
    parser.add_argument("--zip", type=Path, default=None, help="Дополнительно записать zip рядом с указанным путём")
    parser.add_argument("--exported-by", type=str, default=None, help="Поле exported_by в pack.manifest.yml")
    args = parser.parse_args()

    course_slugs = sorted(set(args.course_slugs))
    output = args.output
    if output is None:
        output = Path("exports") / f"{course_slugs[0]}-pack"
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    try:
        bundle = load_content_bundle(
            content_root=CONTENT_ROOT,
            task_root=TASK_ROOT,
            checkpoint_root=CHECKPOINT_ROOT,
            source_root=SOURCE_ROOT,
            raise_on_error=True,
        )
    except ContentValidationException as exc:
        print("Content validation failed (исправьте репозиторий перед export), exit=1", file=sys.stderr)
        for issue in exc.report.errors:
            print(f"- {issue.location}: {issue.message}", file=sys.stderr)
        return 1

    known = {c.schema.slug for c in bundle.courses}
    missing = sorted(set(course_slugs) - known)
    if missing:
        print(f"Неизвестные course slug: {missing}. Доступно: {sorted(known)}", file=sys.stderr)
        return 1

    selected = set(course_slugs)
    courses_out = output / "courses"
    courses_out.mkdir(parents=True, exist_ok=True)

    for slug in course_slugs:
        src = (CONTENT_ROOT / slug).resolve()
        dst = courses_out / slug
        if not src.is_dir():
            print(f"Каталог курса не найден: {src}", file=sys.stderr)
            return 1
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    if args.include_referenced_global_tasks:
        tasks_out = output / "tasks"
        tasks_out.mkdir(parents=True, exist_ok=True)
        for slug, path in _tasks_referenced_by_courses(bundle, selected, TASK_ROOT).items():
            shutil.copy2(path, tasks_out / f"{slug}.yml")

    if args.include_referenced_global_checkpoints:
        cp_out = output / "checkpoints"
        cp_out.mkdir(parents=True, exist_ok=True)
        for slug, path in _checkpoints_referenced_by_courses(bundle, selected, CHECKPOINT_ROOT).items():
            shutil.copy2(path, cp_out / f"{slug}.yml")

    if args.include_sources:
        reg = SOURCE_ROOT / "source_registry.yml"
        if not reg.is_file():
            print(f"Не найден source_registry.yml: {reg}", file=sys.stderr)
            return 1
        sources_out = output / "sources"
        sources_out.mkdir(parents=True, exist_ok=True)
        shutil.copy2(reg, sources_out / "source_registry.yml")

    primary_title = next(c.schema.title for c in bundle.courses if c.schema.slug == course_slugs[0])
    pack_slug = f"{course_slugs[0]}-pack" if len(course_slugs) == 1 else "multi-course-pack"

    write_pack_manifest(
        output / "pack.manifest.yml",
        pack_slug=pack_slug,
        pack_title=primary_title if len(course_slugs) == 1 else "Multi course pack",
        course_slugs=course_slugs,
        sources_included=bool(args.include_sources),
        validated=False,
        exported_by=args.exported_by,
    )

    if args.zip:
        zip_path = args.zip.resolve()
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        _zip_pack(output, zip_path)

    print(f"[OK] pack записан в {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
