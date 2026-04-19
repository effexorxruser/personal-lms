from __future__ import annotations

from pathlib import Path

import yaml

from app.content_pipeline import validate_content
from tests.content_test_utils import create_valid_content_tree, write_lesson, write_yaml


def test_duplicate_lesson_key_fails_validation(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)
    module_dir = tree["module_dir"]

    write_lesson(
        module_dir / "lessons" / "another-lesson.md",
        key="demo-intro",
        title="Duplicate Key",
        summary="Дубликат ключа.",
        body="# Duplicate\n\nBody",
    )
    module_payload = yaml.safe_load((module_dir / "module.yml").read_text(encoding="utf-8"))
    module_payload["lessons"].append("another-lesson")
    write_yaml(module_dir / "module.yml", module_payload)

    report = validate_content(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
    )

    assert not report.ok
    assert any("duplicate lesson.key" in issue.message for issue in report.errors)


def test_broken_task_reference_fails_validation(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)
    lesson_path = tree["module_dir"] / "lessons" / "demo-intro.md"
    text = lesson_path.read_text(encoding="utf-8").replace("task_slug: demo-task", "task_slug: missing-task")
    lesson_path.write_text(text, encoding="utf-8")

    report = validate_content(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
    )

    assert not report.ok
    assert any("task_slug" in issue.message and "missing-task" in issue.message for issue in report.errors)


def test_broken_checkpoint_module_reference_fails_validation(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)

    checkpoint_path = tree["checkpoint_root"] / "demo-checkpoint.yml"
    payload = yaml.safe_load(checkpoint_path.read_text(encoding="utf-8"))
    payload["module_slug"] = "unknown-module"
    write_yaml(checkpoint_path, payload)

    report = validate_content(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
    )

    assert not report.ok
    assert any("module_slug" in issue.message and "unknown-module" in issue.message for issue in report.errors)


def test_missing_lesson_file_from_module_list_fails_validation(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)

    module_path = tree["module_dir"] / "module.yml"
    payload = yaml.safe_load(module_path.read_text(encoding="utf-8"))
    payload["lessons"].append("missing-lesson")
    write_yaml(module_path, payload)

    report = validate_content(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
    )

    assert not report.ok
    assert any("missing-lesson" in issue.message and "не найден" in issue.message for issue in report.errors)


def test_orphan_lesson_file_is_detected(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)

    write_lesson(
        tree["module_dir"] / "lessons" / "orphan.md",
        key="orphan",
        title="Orphan",
        summary="Сирота",
        body="# Orphan\n\nBody",
    )

    report = validate_content(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
    )

    assert not report.ok
    assert any("orphan lesson file" in issue.message for issue in report.errors)


def test_empty_module_or_course_is_detected(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)

    course_manifest = tree["course_dir"] / "course.yml"
    module_manifest = tree["module_dir"] / "module.yml"

    course_payload = yaml.safe_load(course_manifest.read_text(encoding="utf-8"))
    module_payload = yaml.safe_load(module_manifest.read_text(encoding="utf-8"))
    course_payload["modules"] = []
    module_payload["lessons"] = []
    write_yaml(course_manifest, course_payload)
    write_yaml(module_manifest, module_payload)

    report = validate_content(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
    )

    assert not report.ok
    assert any("modules" in issue.message for issue in report.errors)
    assert any("хотя бы один урок" in issue.message for issue in report.errors)
