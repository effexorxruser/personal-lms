"""Optional pack.manifest.yml (operational metadata; not used by LMS runtime)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.content_pipeline import SUPPORTED_CONTENT_SCHEMA_VERSION


class PackInfoBlock(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    slug: str
    title: str
    exported_at: str | None = None
    exported_by: str | None = None
    contract_version: int = SUPPORTED_CONTENT_SCHEMA_VERSION


class SourcesBlock(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    included: bool = False


class ChecksBlock(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    validated: bool = False


class CoursePackManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    schema_version: int = 1
    pack: PackInfoBlock
    courses: list[str] = Field(min_length=1)
    sources: SourcesBlock | None = None
    checks: ChecksBlock | None = None

    @field_validator("schema_version")
    @classmethod
    def supported_schema(cls, value: int) -> int:
        if value != 1:
            raise ValueError("pack.manifest.yml: поддерживается только schema_version: 1")
        return value


def load_optional_pack_manifest(pack_root: Path) -> CoursePackManifest | None:
    path = pack_root / "pack.manifest.yml"
    if not path.is_file():
        return None
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("pack.manifest.yml: ожидался YAML-объект (mapping)")
    return CoursePackManifest.model_validate(raw)


def write_pack_manifest(
    path: Path,
    *,
    pack_slug: str,
    pack_title: str,
    course_slugs: list[str],
    sources_included: bool,
    validated: bool,
    exported_by: str | None,
) -> None:
    payload = {
        "schema_version": 1,
        "pack": {
            "slug": pack_slug,
            "title": pack_title,
            "exported_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "exported_by": exported_by or None,
            "contract_version": SUPPORTED_CONTENT_SCHEMA_VERSION,
        },
        "courses": sorted(course_slugs),
        "sources": {"included": sources_included},
        "checks": {"validated": validated},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
