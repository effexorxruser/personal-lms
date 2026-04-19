from __future__ import annotations

from pathlib import Path

import yaml

from app.content_pipeline import load_content_bundle, validate_content
from tests.content_test_utils import create_valid_content_tree, write_yaml


def test_current_content_snapshot_is_valid() -> None:
    report = validate_content()
    assert report.ok


def test_missing_required_field_fails_validation(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)

    task_path = tree["task_root"] / "demo-task.yml"
    payload = yaml.safe_load(task_path.read_text(encoding="utf-8"))
    del payload["title"]
    write_yaml(task_path, payload)

    report = validate_content(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
    )

    assert not report.ok
    assert any("demo-task.yml" in issue.location and "title" in issue.message for issue in report.errors)


def test_invalid_enum_value_fails_validation(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)

    task_path = tree["task_root"] / "demo-task.yml"
    payload = yaml.safe_load(task_path.read_text(encoding="utf-8"))
    payload["submission_type"] = "essay"
    write_yaml(task_path, payload)

    report = validate_content(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
    )

    assert not report.ok
    assert any("submission_type" in issue.message for issue in report.errors)


def test_empty_lesson_body_fails_validation(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)
    lesson_path = tree["module_dir"] / "lessons" / "demo-intro.md"

    lesson_path.write_text(
        "---\n"
        "key: demo-intro\n"
        'title: "Demo Intro"\n'
        "summary: Старт\n"
        "objectives:\n"
        "  - Проверить\n"
        "checklist:\n"
        "  - Проверить\n"
        "task_slug: demo-task\n"
        "---\n",
        encoding="utf-8",
    )

    report = validate_content(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
    )

    assert not report.ok
    assert any("markdown body" in issue.message for issue in report.errors)


def test_invalid_task_terminal_config_fails_validation(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)

    task_path = tree["task_root"] / "demo-task.yml"
    payload = yaml.safe_load(task_path.read_text(encoding="utf-8"))
    payload["terminal"] = {
        "enabled": True,
        "presets": [{"label": "Пуск", "command": "run"}],
        "allow_manual_input": True,
        "allowed_commands": [""],
    }
    write_yaml(task_path, payload)

    report = validate_content(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
    )

    assert not report.ok
    assert any("allowed_commands" in issue.message for issue in report.errors)


def test_loader_contract_uses_the_same_validated_bundle(tmp_path: Path) -> None:
    tree = create_valid_content_tree(tmp_path)

    bundle = load_content_bundle(
        content_root=tree["content_root"],
        task_root=tree["task_root"],
        checkpoint_root=tree["checkpoint_root"],
        raise_on_error=True,
    )

    assert bundle.report.ok
    assert bundle.report.stats.courses == 1
    assert bundle.report.stats.lessons == 1
