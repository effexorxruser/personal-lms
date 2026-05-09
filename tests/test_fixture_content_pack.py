"""Регрессия: закоммиченный content pack проходит validate_content."""

from __future__ import annotations

from app.content_pipeline import validate_content
from tests.fixture_metadata import CONTENT_PACK_ROOT


def test_committed_fixture_content_pack_validates_cleanly() -> None:
    root = CONTENT_PACK_ROOT
    report = validate_content(
        content_root=root / "courses",
        task_root=root / "tasks",
        checkpoint_root=root / "checkpoints-global",
        source_root=root / "sources",
    )
    assert report.ok
