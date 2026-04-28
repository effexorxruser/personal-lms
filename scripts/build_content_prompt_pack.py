#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
import re
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.content_pipeline import BLUEPRINT_ROOT, SOURCE_ROOT
from app.source_fetcher import CACHE_ROOT, list_sources

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_ROOT = PROJECT_ROOT / "content_builder" / "prompts"
RULES_ROOT = PROJECT_ROOT / "content_builder" / "rules"
SCHEMAS_ROOT = PROJECT_ROOT / "content_builder" / "schemas"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "content_drafts"
DEFAULT_BLUEPRINT = BLUEPRINT_ROOT / "backend_developer_6_months.yml"


class PromptPackBuildError(ValueError):
    pass


def _now_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _load_yaml(path: Path):
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PromptPackBuildError(f"file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise PromptPackBuildError(f"invalid yaml in {path}: {exc}") from exc
    return payload


def _find_blueprint_module(blueprint_path: Path, block: int, module_slug: str) -> tuple[str, dict]:
    payload = _load_yaml(blueprint_path)
    if not isinstance(payload, dict):
        raise PromptPackBuildError("blueprint must be yaml mapping")
    blocks = payload.get("blocks")
    if not isinstance(blocks, list):
        raise PromptPackBuildError("blueprint missing blocks list")

    for block_item in blocks:
        if not isinstance(block_item, dict):
            continue
        if block_item.get("block") != block:
            continue
        block_title = str(block_item.get("title", "")).strip()
        modules = block_item.get("modules")
        if not isinstance(modules, list):
            continue
        for module in modules:
            if isinstance(module, dict) and module.get("slug") == module_slug:
                return block_title, module

    raise PromptPackBuildError(f"module not found in blueprint: block={block}, module={module_slug}")


def _load_latest_cache_runs(cache_manifest_path: Path | None, source_ids: list[str]) -> dict[str, dict]:
    if cache_manifest_path is None or not cache_manifest_path.exists():
        return {}
    payload = _load_yaml(cache_manifest_path)
    if not isinstance(payload, dict):
        return {}
    runs = payload.get("runs")
    if not isinstance(runs, list):
        return {}
    latest: dict[str, dict] = {}
    for item in runs:
        if not isinstance(item, dict):
            continue
        source_id = str(item.get("source_id", "")).strip()
        if source_id not in source_ids:
            continue
        latest[source_id] = item
    return latest


def _sanitize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")


def _render_template(path: Path, replacements: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def build_prompt_pack(
    *,
    block: int,
    module_slug: str,
    blueprint_path: Path = DEFAULT_BLUEPRINT,
    source_root: Path = SOURCE_ROOT,
    cache_manifest_path: Path | None = CACHE_ROOT / "manifest.yml",
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> Path:
    block_title, module = _find_blueprint_module(blueprint_path, block, module_slug)
    sources = list_sources(source_root=source_root)

    required_source_ids = [str(item) for item in module.get("required_source_ids", [])]
    expected_tasks = [str(item) for item in module.get("expected_tasks", [])]
    checkpoint_slug = str(module.get("checkpoint_slug", "")).strip()
    expected_artifact = str(module.get("expected_artifact", "")).strip()

    unknown_source_ids = [item for item in required_source_ids if item not in sources]
    if unknown_source_ids:
        raise PromptPackBuildError(f"module contains unknown source ids: {', '.join(unknown_source_ids)}")

    cache_summary = _load_latest_cache_runs(cache_manifest_path, required_source_ids)

    stamp = _now_stamp()
    pack_dir = output_root / "prompt_packs" / f"block-{block}-{_sanitize_name(module_slug)}-{stamp}"
    prompts_dir = pack_dir / "prompts"
    rules_dir = pack_dir / "rules"
    schemas_dir = pack_dir / "schemas"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    rules_dir.mkdir(parents=True, exist_ok=True)
    schemas_dir.mkdir(parents=True, exist_ok=True)

    replacements = {
        "BLOCK_NUMBER": str(block),
        "MODULE_SLUG": module_slug,
        "BLOCK_TITLE": block_title,
        "EXPECTED_ARTIFACT": expected_artifact,
        "REQUIRED_SOURCE_IDS": ", ".join(required_source_ids) if required_source_ids else "-",
        "EXPECTED_TASKS": ", ".join(expected_tasks) if expected_tasks else "-",
        "CHECKPOINT_SLUG": checkpoint_slug or "checkpoint-slug-required",
        "ALLOWED_SOURCE_IDS": ", ".join(sorted(sources.keys())),
        "LESSON_KEY_HINT": f"{module_slug}-lesson-key",
        "TASK_SLUG_HINT": expected_tasks[0] if expected_tasks else f"{module_slug}-task",
    }

    prompt_files = [
        "build_module.md",
        "build_lesson.md",
        "build_task.md",
        "build_checkpoint.md",
        "validate_draft.md",
    ]
    for filename in prompt_files:
        rendered = _render_template(PROMPTS_ROOT / filename, replacements)
        (prompts_dir / filename).write_text(rendered, encoding="utf-8")

    for filename in [
        "russian_friendly.md",
        "technical_english.md",
        "isolated_platform.md",
        "student_friendly.md",
        "no_manual_source_hunting.md",
    ]:
        (rules_dir / filename).write_text((RULES_ROOT / filename).read_text(encoding="utf-8"), encoding="utf-8")

    for filename in ["prompt_pack.schema.yml", "draft_output_contract.yml"]:
        (schemas_dir / filename).write_text((SCHEMAS_ROOT / filename).read_text(encoding="utf-8"), encoding="utf-8")

    output_contract = _load_yaml(SCHEMAS_ROOT / "draft_output_contract.yml")
    required_sections = output_contract.get("lesson", {}).get("required_sections", [])
    if not isinstance(required_sections, list):
        required_sections = []

    pack_payload = {
        "version": "v1",
        "block": block,
        "module_slug": module_slug,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "inputs": {
            "blueprint_path": str(blueprint_path),
            "source_registry_path": str(source_root / "source_registry.yml"),
            "source_cache_manifest_path": str(cache_manifest_path) if cache_manifest_path and cache_manifest_path.exists() else None,
            "required_source_ids": required_source_ids,
            "expected_tasks": expected_tasks,
            "checkpoint_slug": checkpoint_slug,
            "expected_artifact": expected_artifact,
            "required_lesson_sections": required_sections,
            "draft_output_contract": output_contract,
            "source_cache_latest": cache_summary,
        },
        "prompts": {
            "build_module": "prompts/build_module.md",
            "build_lesson": "prompts/build_lesson.md",
            "build_task": "prompts/build_task.md",
            "build_checkpoint": "prompts/build_checkpoint.md",
            "validate_draft": "prompts/validate_draft.md",
        },
        "rules": [
            "rules/russian_friendly.md",
            "rules/technical_english.md",
            "rules/isolated_platform.md",
            "rules/student_friendly.md",
            "rules/no_manual_source_hunting.md",
        ],
        "output_contract": "schemas/draft_output_contract.yml",
    }
    (pack_dir / "prompt_pack.yml").write_text(
        yaml.safe_dump(pack_payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return pack_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Build content builder prompt pack for a blueprint module.")
    parser.add_argument("--block", type=int, required=True, help="Block number from blueprint")
    parser.add_argument("--module", required=True, help="Module slug from blueprint")
    parser.add_argument("--blueprint", type=Path, default=DEFAULT_BLUEPRINT, help="Path to blueprint yml")
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT, help="Path to source registry root")
    parser.add_argument(
        "--cache-manifest",
        type=Path,
        default=CACHE_ROOT / "manifest.yml",
        help="Optional cache manifest path (may not exist)",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT, help="Root folder for prompt packs")
    args = parser.parse_args()

    cache_manifest = args.cache_manifest if args.cache_manifest.exists() else None
    try:
        pack_dir = build_prompt_pack(
            block=args.block,
            module_slug=args.module,
            blueprint_path=args.blueprint,
            source_root=args.source_root,
            cache_manifest_path=cache_manifest,
            output_root=args.output_root,
        )
    except PromptPackBuildError as exc:
        print(f"error: {exc}")
        return 1

    print(f"Prompt pack created: {pack_dir}")
    print("Use files under this directory with Cursor/Codex/ChatGPT for draft generation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
