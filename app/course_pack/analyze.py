"""Analyze a portable course pack directory: validate graph + manifest + target conflicts."""

from __future__ import annotations

import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import yaml
from pydantic import ValidationError

from app.content_pipeline import (
    CHECKPOINT_ROOT,
    CONTENT_ROOT,
    SOURCE_ROOT,
    TASK_ROOT,
    ContentBundle,
    ContentValidationIssue,
    SUPPORTED_CONTENT_SCHEMA_VERSION,
    load_content_bundle,
    validate_content,
)
from app.course_pack.import_report import CoursePackImportReport
from app.course_pack.manifest import CoursePackManifest

MANIFEST_FILENAME = "pack.manifest.yml"


def list_pack_course_slugs(pack_courses_root: Path) -> list[str]:
    if not pack_courses_root.is_dir():
        return []
    return sorted({p.parent.name for p in pack_courses_root.glob("*/course.yml")})


def _resolve_pack_checkpoint_dir(pack_root: Path) -> Path | None:
    for rel in ("checkpoints", "checkpoints-global"):
        candidate = pack_root / rel
        if candidate.is_dir():
            return candidate
    return None


def analyze_pack_roots(pack_root: Path) -> tuple[Path, Path | None, Path | None, Path]:
    courses = pack_root / "courses"
    tasks = pack_root / "tasks"
    checkpoints = _resolve_pack_checkpoint_dir(pack_root)
    sources = pack_root / "sources"
    return courses, tasks, checkpoints, sources


def resolve_pack_source_root(pack_root: Path, *, fallback_source_root: Path = SOURCE_ROOT) -> Path:
    reg = pack_root / "sources" / "source_registry.yml"
    if reg.is_file():
        return pack_root / "sources"
    return fallback_source_root


@contextmanager
def pack_validation_roots(
    pack_root: Path,
    *,
    fallback_source_root: Path = SOURCE_ROOT,
) -> Iterator[tuple[Path, Path, Path, Path]]:
    courses, tasks_optional, checkpoints_optional, _sources_placeholder = analyze_pack_roots(pack_root)
    if not courses.is_dir():
        raise ValueError(f"pack: отсутствует каталог courses/: {courses}")

    source_root = resolve_pack_source_root(pack_root, fallback_source_root=fallback_source_root)

    task_root = tasks_optional if tasks_optional and tasks_optional.is_dir() else None
    ck_root = checkpoints_optional if checkpoints_optional and checkpoints_optional.is_dir() else None

    if task_root is None and ck_root is None:
        with tempfile.TemporaryDirectory(prefix="plms-pack-task-") as td_t, tempfile.TemporaryDirectory(
            prefix="plms-pack-cp-",
        ) as td_c:
            yield courses, Path(td_t), Path(td_c), source_root
        return
    if task_root is None:
        with tempfile.TemporaryDirectory(prefix="plms-pack-task-") as td_t:
            yield courses, Path(td_t), ck_root, source_root
        return
    if ck_root is None:
        with tempfile.TemporaryDirectory(prefix="plms-pack-cp-") as td_c:
            yield courses, task_root, Path(td_c), source_root
        return

    yield courses, task_root, ck_root, source_root


def _load_manifest_issues(pack_root: Path) -> tuple[CoursePackManifest | None, list[ContentValidationIssue], list[ContentValidationIssue]]:
    path = pack_root / MANIFEST_FILENAME
    if not path.is_file():
        return None, [], []
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        issue = ContentValidationIssue(MANIFEST_FILENAME, f"manifest: ошибка чтения: {exc}")
        return None, [], [issue]
    except yaml.YAMLError as exc:
        issue = ContentValidationIssue(MANIFEST_FILENAME, f"manifest: ошибка YAML: {exc}")
        return None, [], [issue]
    if raw is None:
        return None, [], []
    if not isinstance(raw, dict):
        return None, [], [ContentValidationIssue(MANIFEST_FILENAME, "manifest: ожидался YAML mapping")]
    try:
        return CoursePackManifest.model_validate(raw), [], []
    except ValidationError as exc:
        errs: list[ContentValidationIssue] = []
        for item in exc.errors():
            location = ".".join(str(part) for part in item.get("loc", ()))
            message = str(item.get("msg", "некорректное значение"))
            details = f"{location}: {message}" if location else message
            errs.append(ContentValidationIssue(MANIFEST_FILENAME, details))
        return None, errs, []


def manifest_consistency_issues(
    manifest: CoursePackManifest | None,
    *,
    pack_root: Path,
    pack_course_slugs: list[str],
) -> tuple[list[ContentValidationIssue], list[ContentValidationIssue]]:
    errors: list[ContentValidationIssue] = []
    warnings: list[ContentValidationIssue] = []
    if manifest is None:
        return errors, warnings

    if manifest.pack.contract_version != SUPPORTED_CONTENT_SCHEMA_VERSION:
        warnings.append(
            ContentValidationIssue(
                MANIFEST_FILENAME,
                (
                    "manifest.pack.contract_version отличается от поддерживаемой версии контента: "
                    f"{manifest.pack.contract_version} (ожидалось {SUPPORTED_CONTENT_SCHEMA_VERSION})"
                ),
            )
        )

    declared = set(manifest.courses)
    actual = set(pack_course_slugs)
    missing = sorted(declared - actual)
    extra = sorted(actual - declared)
    if missing:
        errors.append(
            ContentValidationIssue(
                MANIFEST_FILENAME,
                f"manifest: объявлены курсы, отсутствующие в pack/courses: {missing}",
            )
        )
    if extra:
        warnings.append(
            ContentValidationIssue(
                MANIFEST_FILENAME,
                f"manifest: есть курсы в pack/courses без записи в manifest: {extra}",
            )
        )

    reg_in_pack = (pack_root / "sources" / "source_registry.yml").is_file()
    if manifest.sources and manifest.sources.included and not reg_in_pack:
        warnings.append(
            ContentValidationIssue(
                MANIFEST_FILENAME,
                "manifest.sources.included=true, но sources/source_registry.yml в паке отсутствует",
            )
        )

    return errors, warnings


def detect_target_conflicts(
    pack_bundle: ContentBundle,
    *,
    target_content_root: Path,
    target_task_root: Path,
    target_checkpoint_root: Path,
    target_source_root: Path,
) -> tuple[list[ContentValidationIssue], list[ContentValidationIssue]]:
    errors: list[ContentValidationIssue] = []
    warnings: list[ContentValidationIssue] = []

    target_bundle = load_content_bundle(
        content_root=target_content_root,
        task_root=target_task_root,
        checkpoint_root=target_checkpoint_root,
        source_root=target_source_root,
        raise_on_error=False,
    )

    pack_course_slugs = {c.schema.slug for c in pack_bundle.courses}
    existing_target_slugs = set(list_pack_course_slugs(target_content_root))
    for slug in sorted(pack_course_slugs & existing_target_slugs):
        errors.append(
            ContentValidationIssue(
                str(target_content_root.resolve()),
                f"конфликт импорта: курс с slug {slug!r} уже есть в целевом catalog",
            )
        )

    for key in sorted(set(pack_bundle.lessons_by_key) & set(target_bundle.lessons_by_key)):
        errors.append(
            ContentValidationIssue(
                "import:lesson-keys",
                f"конфликт импорта: lesson.key {key!r} уже используется в целевом catalog",
            )
        )

    target_task_slugs = {p.stem for p in target_task_root.glob("*.yml")}
    pack_global_tasks = pack_bundle.tasks_by_slug.keys()
    for slug in sorted(set(pack_global_tasks) & target_task_slugs):
        errors.append(
            ContentValidationIssue(
                str((target_task_root / f"{slug}.yml").resolve()),
                f"конфликт импорта: task.slug {slug!r} уже есть в целевом tasks/",
            )
        )

    target_checkpoint_slugs = {p.stem for p in target_checkpoint_root.glob("*.yml")}
    pack_global_cps = pack_bundle.checkpoints_by_slug.keys()
    for slug in sorted(set(pack_global_cps) & target_checkpoint_slugs):
        errors.append(
            ContentValidationIssue(
                str((target_checkpoint_root / f"{slug}.yml").resolve()),
                f"конфликт импорта: checkpoint.slug {slug!r} уже есть в целевом checkpoints/",
            )
        )

    return errors, warnings


def build_course_pack_import_report(
    pack_root: Path,
    *,
    target_content_root: Path | None = None,
    target_task_root: Path | None = None,
    target_checkpoint_root: Path | None = None,
    target_source_root: Path | None = None,
    fallback_source_root_for_pack: Path = SOURCE_ROOT,
) -> CoursePackImportReport:
    resolved_target_content = CONTENT_ROOT if target_content_root is None else target_content_root
    resolved_task = TASK_ROOT if target_task_root is None else target_task_root
    resolved_cp = CHECKPOINT_ROOT if target_checkpoint_root is None else target_checkpoint_root
    resolved_src = SOURCE_ROOT if target_source_root is None else target_source_root

    manifest, manifest_parse_errors, manifest_parse_warnings = _load_manifest_issues(pack_root)
    manifest_warnings = [*manifest_parse_warnings]
    manifest_errors = [*manifest_parse_errors]

    if manifest_parse_errors:
        manifest = None

    detected_slugs_pre = list_pack_course_slugs(pack_root / "courses")
    m_err, m_warn = manifest_consistency_issues(manifest, pack_root=pack_root, pack_course_slugs=detected_slugs_pre)
    manifest_errors.extend(m_err)
    manifest_warnings.extend(m_warn)

    with pack_validation_roots(pack_root, fallback_source_root=fallback_source_root_for_pack) as (
        courses_r,
        task_r,
        cp_r,
        source_r,
    ):
        bundle = load_content_bundle(
            content_root=courses_r,
            task_root=task_r,
            checkpoint_root=cp_r,
            source_root=source_r,
            raise_on_error=False,
        )
        report = bundle.report
        detected_courses = sorted({c.schema.slug for c in bundle.courses})
        if not detected_courses:
            detected_courses = detected_slugs_pre

        conflict_e, conflict_w = detect_target_conflicts(
            bundle,
            target_content_root=resolved_target_content,
            target_task_root=resolved_task,
            target_checkpoint_root=resolved_cp,
            target_source_root=resolved_src,
        )

    manifest_present = (pack_root / MANIFEST_FILENAME).is_file()
    contract_version = manifest.pack.contract_version if manifest else None

    return CoursePackImportReport.from_parts(
        graph_errors=list(report.errors),
        graph_warnings=list(report.warnings),
        stats=report.stats,
        course_slugs=detected_courses,
        manifest_present=manifest_present,
        contract_version=contract_version,
        conflict_errors=conflict_e,
        conflict_warnings=conflict_w,
        manifest_warnings=manifest_warnings,
        manifest_errors=manifest_errors,
    )


def run_pack_graph_validation(
    pack_root: Path,
    *,
    fallback_source_root: Path = SOURCE_ROOT,
) -> object:
    with pack_validation_roots(pack_root, fallback_source_root=fallback_source_root) as (
        courses_r,
        task_r,
        cp_r,
        source_r,
    ):
        return validate_content(
            content_root=courses_r,
            task_root=task_r,
            checkpoint_root=cp_r,
            source_root=source_r,
        )
