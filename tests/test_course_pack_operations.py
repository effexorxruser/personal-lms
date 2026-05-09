"""Stage 7: операции course pack (analyze, export, preflight, конфликты с target)."""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import app.content_pipeline as content_pipeline
import pytest

from app.course_pack.manifest import write_pack_manifest
from app.services.course_pack_preview_service import preview_course_pack
from tests.fixture_metadata import CONTENT_PACK_ROOT


def _sync_pack(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def test_fixture_pack_without_manifest_is_compatible() -> None:
    report = preview_course_pack(CONTENT_PACK_ROOT)
    assert report.compatible
    assert not report.manifest_present


def test_corrupt_manifest_is_reported(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    _sync_pack(CONTENT_PACK_ROOT, pack)
    (pack / "pack.manifest.yml").write_text(
        "schema_version: 2\npack:\n  slug: bad\n  title: Bad\n  contract_version: 1\ncourses: [test-python-course]\n",
        encoding="utf-8",
    )
    report = preview_course_pack(pack)
    assert not report.compatible
    assert any("manifest" in e.location for e in report.errors)


def test_manifest_course_mismatch_error(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    _sync_pack(CONTENT_PACK_ROOT, pack)
    write_pack_manifest(
        pack / "pack.manifest.yml",
        pack_slug="x-pack",
        pack_title="Test",
        course_slugs=["nonexistent-course"],
        sources_included=False,
        validated=False,
        exported_by=None,
    )
    report = preview_course_pack(pack)
    assert not report.compatible
    msgs = [e.message for e in report.errors]
    assert any("объявлены курсы" in m and "pack/courses" in m for m in msgs)


def test_course_slug_conflict_with_target(tmp_path: Path) -> None:
    pack = tmp_path / "pack-a"
    target_courses = tmp_path / "target" / "courses"
    target_courses.mkdir(parents=True)
    _sync_pack(CONTENT_PACK_ROOT, pack)
    _sync_pack(CONTENT_PACK_ROOT / "courses" / "test-python-course", target_courses / "test-python-course")

    report = preview_course_pack(
        pack,
        target_content_root=target_courses,
        target_task_root=CONTENT_PACK_ROOT / "tasks",
        target_checkpoint_root=CONTENT_PACK_ROOT / "checkpoints-global",
        target_source_root=CONTENT_PACK_ROOT / "sources",
    )
    assert not report.compatible
    assert any("уже есть в целевом catalog" in e.message for e in report.errors)


def test_duplicate_lesson_key_conflict_with_target(tmp_path: Path) -> None:
    """Курс переименован (другой slug), но ключи уроков совпадают с уже существующим курсом в target."""

    pack = tmp_path / "imp"
    _sync_pack(CONTENT_PACK_ROOT, pack)
    shutil.copytree(
        pack / "courses" / "test-python-course",
        pack / "courses" / "alternate-python-course",
    )
    course_yml = pack / "courses" / "alternate-python-course" / "course.yml"
    text = course_yml.read_text(encoding="utf-8")
    course_yml.write_text(text.replace("slug: test-python-course", "slug: alternate-python-course"), encoding="utf-8")
    shutil.rmtree(pack / "courses" / "test-python-course")

    report = preview_course_pack(
        pack,
        target_content_root=CONTENT_PACK_ROOT / "courses",
        target_task_root=CONTENT_PACK_ROOT / "tasks",
        target_checkpoint_root=CONTENT_PACK_ROOT / "checkpoints-global",
        target_source_root=CONTENT_PACK_ROOT / "sources",
    )
    assert not report.compatible
    assert any("lesson.key" in e.message for e in report.errors)


def test_preview_does_not_mutate_marker_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target_courses = tmp_path / "tgt" / "courses"
    target_courses.mkdir(parents=True)
    marker = target_courses / "marker.txt"
    marker.write_text("x", encoding="utf-8")

    pack = tmp_path / "minimal"
    (pack / "courses").mkdir(parents=True)

    monkeypatch.setattr(content_pipeline, "CONTENT_ROOT", target_courses.resolve())
    monkeypatch.setattr(content_pipeline, "TASK_ROOT", CONTENT_PACK_ROOT / "tasks")
    monkeypatch.setattr(content_pipeline, "CHECKPOINT_ROOT", CONTENT_PACK_ROOT / "checkpoints-global")
    monkeypatch.setattr(content_pipeline, "SOURCE_ROOT", CONTENT_PACK_ROOT / "sources")

    before = marker.read_text(encoding="utf-8")
    preview_course_pack(pack)
    assert marker.read_text(encoding="utf-8") == before


def test_export_script_creates_pack(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(content_pipeline, "CONTENT_ROOT", CONTENT_PACK_ROOT / "courses")
    monkeypatch.setattr(content_pipeline, "TASK_ROOT", CONTENT_PACK_ROOT / "tasks")
    monkeypatch.setattr(content_pipeline, "CHECKPOINT_ROOT", CONTENT_PACK_ROOT / "checkpoints-global")
    monkeypatch.setattr(content_pipeline, "SOURCE_ROOT", CONTENT_PACK_ROOT / "sources")

    out = tmp_path / "my-pack"
    script_path = repo / "scripts" / "export_course_pack.py"
    spec = importlib.util.spec_from_file_location("_export_course_pack_script", script_path)
    assert spec and spec.loader
    export_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(export_mod)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "export_course_pack.py",
            "--course-slug",
            "test-python-course",
            "--output",
            str(out),
            "--include-sources",
            "--include-referenced-global-tasks",
            "--include-referenced-global-checkpoints",
        ],
    )

    assert export_mod.main() == 0

    cy = out / "courses" / "test-python-course" / "course.yml"
    assert cy.is_file()
    assert (out / "pack.manifest.yml").is_file()
    assert (out / "sources" / "source_registry.yml").is_file()
