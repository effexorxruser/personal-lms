"""Read-only превью course pack перед импортом (операционный overlay, без записи на диск и без БД)."""

from __future__ import annotations

from pathlib import Path

from app.course_pack.analyze import build_course_pack_import_report
from app.course_pack.import_report import CoursePackImportReport


def preview_course_pack(
    pack_root: Path,
    *,
    target_content_root: Path | None = None,
    target_task_root: Path | None = None,
    target_checkpoint_root: Path | None = None,
    target_source_root: Path | None = None,
) -> CoursePackImportReport:
    """
    Учитывает `pack.manifest.yml`, если файл есть рядом с `courses/`; runtime LMS этот файл не читает.

    Если любой из корней target не указан — для проверки конфликтов импорта используются корни текущего
    репозитория из `content_pipeline` (`CONTENT_ROOT`, `TASK_ROOT`, и т.д.).
    """

    resolved_pack = pack_root.resolve()
    return build_course_pack_import_report(
        resolved_pack,
        target_content_root=target_content_root,
        target_task_root=target_task_root,
        target_checkpoint_root=target_checkpoint_root,
        target_source_root=target_source_root,
    )
