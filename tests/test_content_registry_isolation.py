"""Изоляция get_content_registry при смене content roots между тестами."""

from __future__ import annotations

from app.content_registry import get_content_registry
from tests.content_runtime_utils import use_empty_catalog, use_fixture_content_pack
from tests.fixture_metadata import ACTIVE_COURSE_SLUG


def test_fixture_then_empty_catalog_no_stale_course(monkeypatch, tmp_path) -> None:
    use_fixture_content_pack(monkeypatch)
    assert ACTIVE_COURSE_SLUG in get_content_registry().courses
    use_empty_catalog(monkeypatch, tmp_path)
    assert get_content_registry().courses == {}


def test_empty_catalog_then_fixture_loads_course(monkeypatch, tmp_path) -> None:
    use_empty_catalog(monkeypatch, tmp_path)
    assert get_content_registry().courses == {}
    use_fixture_content_pack(monkeypatch)
    assert ACTIVE_COURSE_SLUG in get_content_registry().courses
