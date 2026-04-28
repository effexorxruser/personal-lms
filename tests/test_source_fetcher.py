from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.source_fetcher import SourceNotFoundError, WebFetchResult, fetch_source
from tests.content_test_utils import write_yaml


def _write_registry(source_root: Path, entries: list[dict]) -> None:
    write_yaml(source_root / "source_registry.yml", entries)


def _base_entry(source_id: str, mode: str) -> dict:
    return {
        "id": source_id,
        "title": "Demo Source",
        "type": "core",
        "language": "en",
        "allowed_usage": "backbone",
        "canonical_url": "https://example.com/source",
        "retrieval": {
            "mode": mode,
            "priority": "high",
            "direct_access": True,
            "preferred_sections": ["https://example.com/source/section-a"],
        },
        "usage_policy": {
            "summarize_only": True,
            "quote_limit": "short",
        },
        "notes": "Demo notes",
    }


def test_web_fetch_creates_manifest_and_snapshot(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    cache_root = tmp_path / "cache"
    _write_registry(source_root, [_base_entry("python-docs", "web")])

    calls: list[str] = []

    def fake_fetch_web(**kwargs) -> WebFetchResult:
        calls.append(kwargs["url"])
        return WebFetchResult(status_code=200, body_text="<html>ok</html>", content_length=15)

    runs = fetch_source(
        source_id="python-docs",
        source_root=source_root,
        cache_root=cache_root,
        fetch_web=fake_fetch_web,
    )

    assert len(runs) == 1
    run = runs[0]
    assert run.status == "ok"
    assert run.http_status == 200
    assert run.snapshot_path is not None
    assert calls == ["https://example.com/source"]

    snapshot_path = cache_root / run.snapshot_path
    assert snapshot_path.exists()
    assert snapshot_path.read_text(encoding="utf-8") == "<html>ok</html>"

    manifest = yaml.safe_load((cache_root / "manifest.yml").read_text(encoding="utf-8"))
    assert isinstance(manifest, dict)
    assert len(manifest["runs"]) == 1
    assert manifest["runs"][0]["source_id"] == "python-docs"
    assert manifest["runs"][0]["status"] == "ok"


def test_web_hash_is_stable_for_same_content(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    cache_root = tmp_path / "cache"
    _write_registry(source_root, [_base_entry("python-docs", "web")])

    def fake_fetch_web(**kwargs) -> WebFetchResult:
        return WebFetchResult(status_code=200, body_text="same content", content_length=12)

    run_a = fetch_source(
        source_id="python-docs",
        source_root=source_root,
        cache_root=cache_root,
        fetch_web=fake_fetch_web,
    )[0]
    run_b = fetch_source(
        source_id="python-docs",
        source_root=source_root,
        cache_root=cache_root,
        fetch_web=fake_fetch_web,
    )[0]

    assert run_a.content_hash == run_b.content_hash
    assert run_a.snapshot_path == run_b.snapshot_path


def test_manual_mode_does_not_call_network(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    cache_root = tmp_path / "cache"
    _write_registry(source_root, [_base_entry("manual-source", "manual")])

    def failing_fetch_web(**kwargs) -> WebFetchResult:
        raise AssertionError("network fetch must not be called for manual mode")

    run = fetch_source(
        source_id="manual-source",
        source_root=source_root,
        cache_root=cache_root,
        fetch_web=failing_fetch_web,
    )[0]
    assert run.status == "manual_required"
    assert run.snapshot_path is None


def test_disabled_mode_does_not_call_network(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    cache_root = tmp_path / "cache"
    _write_registry(source_root, [_base_entry("disabled-source", "disabled")])

    def failing_fetch_web(**kwargs) -> WebFetchResult:
        raise AssertionError("network fetch must not be called for disabled mode")

    run = fetch_source(
        source_id="disabled-source",
        source_root=source_root,
        cache_root=cache_root,
        fetch_web=failing_fetch_web,
    )[0]
    assert run.status == "disabled"
    assert run.snapshot_path is None


def test_mcp_mode_returns_controlled_status(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    cache_root = tmp_path / "cache"
    _write_registry(source_root, [_base_entry("openai-docs", "mcp")])

    run = fetch_source(
        source_id="openai-docs",
        source_root=source_root,
        cache_root=cache_root,
    )[0]
    assert run.status == "unsupported_mode"
    assert run.error is not None


def test_invalid_source_id_raises_clear_error(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    _write_registry(source_root, [_base_entry("python-docs", "web")])

    with pytest.raises(SourceNotFoundError, match="unknown source_id"):
        fetch_source(source_id="missing-id", source_root=source_root, cache_root=tmp_path / "cache")


def test_snapshot_path_stays_inside_cache_root(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    cache_root = tmp_path / "cache"
    _write_registry(source_root, [_base_entry("python-docs", "web")])

    def fake_fetch_web(**kwargs) -> WebFetchResult:
        return WebFetchResult(status_code=200, body_text="safe", content_length=4)

    run = fetch_source(
        source_id="python-docs",
        source_root=source_root,
        cache_root=cache_root,
        fetch_web=fake_fetch_web,
    )[0]
    assert run.snapshot_path is not None
    snapshot_abs = (cache_root / run.snapshot_path).resolve()
    assert cache_root.resolve() in [snapshot_abs, *snapshot_abs.parents]
