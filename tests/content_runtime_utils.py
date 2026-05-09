"""Подмена content roots и сброс LRU-кэша registry для изолированных pytest."""

from __future__ import annotations

import shutil
from pathlib import Path

import app.content_pipeline as content_pipeline
from app.content_registry import get_content_registry

from tests.fixture_metadata import CONTENT_PACK_ROOT


def reset_content_registry_cache() -> None:
    get_content_registry.cache_clear()


def patch_content_pipeline_roots(
    monkeypatch,
    *,
    content_root: Path,
    task_root: Path,
    checkpoint_root: Path,
    source_root: Path,
) -> None:
    monkeypatch.setattr(content_pipeline, "CONTENT_ROOT", content_root)
    monkeypatch.setattr(content_pipeline, "TASK_ROOT", task_root)
    monkeypatch.setattr(content_pipeline, "CHECKPOINT_ROOT", checkpoint_root)
    monkeypatch.setattr(content_pipeline, "SOURCE_ROOT", source_root)
    reset_content_registry_cache()


def use_fixture_content_pack(monkeypatch) -> None:
    root = CONTENT_PACK_ROOT
    patch_content_pipeline_roots(
        monkeypatch,
        content_root=root / "courses",
        task_root=root / "tasks",
        checkpoint_root=root / "checkpoints-global",
        source_root=root / "sources",
    )


def prepare_empty_content_layout(base: Path) -> dict[str, Path]:
    courses = base / "courses"
    tasks = base / "tasks"
    checkpoints = base / "checkpoints"
    sources = base / "sources"
    for p in (courses, tasks, checkpoints, sources):
        p.mkdir(parents=True, exist_ok=True)
    shutil.copy(CONTENT_PACK_ROOT / "sources" / "source_registry.yml", sources / "source_registry.yml")
    return {
        "content_root": courses,
        "task_root": tasks,
        "checkpoint_root": checkpoints,
        "source_root": sources,
    }


def use_empty_catalog(monkeypatch, tmp_path: Path) -> dict[str, Path]:
    base = tmp_path / "empty_catalog"
    roots = prepare_empty_content_layout(base)
    patch_content_pipeline_roots(
        monkeypatch,
        content_root=roots["content_root"],
        task_root=roots["task_root"],
        checkpoint_root=roots["checkpoint_root"],
        source_root=roots["source_root"],
    )
    return roots
