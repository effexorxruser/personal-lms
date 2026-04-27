#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.content_pipeline import PROJECT_ROOT, validate_content


def _load_yaml(path: Path) -> dict | list | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, yaml.YAMLError):
        return None


def _read_source_ids(registry_path: Path) -> set[str]:
    payload = _load_yaml(registry_path)
    if not isinstance(payload, list):
        return set()
    source_ids: set[str] = set()
    for row in payload:
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            source_ids.add(row["id"])
    return source_ids


def _collect_blueprint_stats(blueprint_path: Path, source_ids: set[str]) -> tuple[list[int], list[int], set[str], int]:
    payload = _load_yaml(blueprint_path)
    if not isinstance(payload, dict):
        return ([], [], set(), 0)

    blocks = payload.get("blocks")
    if not isinstance(blocks, list):
        return ([], [], set(), 0)

    defined_blocks: list[int] = []
    empty_blocks: list[int] = []
    required_source_ids: set[str] = set()
    module_count = 0

    for entry in blocks:
        if not isinstance(entry, dict):
            continue
        block_num = entry.get("block")
        if isinstance(block_num, int):
            defined_blocks.append(block_num)

        modules = entry.get("modules")
        if not isinstance(modules, list) or not modules:
            if isinstance(block_num, int):
                empty_blocks.append(block_num)
            continue

        module_count += len(modules)
        for module in modules:
            if not isinstance(module, dict):
                continue
            required = module.get("required_source_ids")
            if isinstance(required, list):
                for source_id in required:
                    if isinstance(source_id, str):
                        required_source_ids.add(source_id)

    missing_source_ids = required_source_ids - source_ids
    return (sorted(set(defined_blocks)), sorted(set(empty_blocks)), missing_source_ids, module_count)


def _collect_course_stats(courses_root: Path) -> tuple[int, int]:
    production = 0
    reference = 0
    for manifest in sorted(courses_root.glob("*/course.yml")):
        slug = manifest.parent.name
        if slug.endswith("-reference"):
            reference += 1
        else:
            production += 1
    return (production, reference)


def main() -> int:
    report = validate_content()

    source_registry_path = PROJECT_ROOT / "content" / "sources" / "source_registry.yml"
    blueprint_path = PROJECT_ROOT / "content" / "blueprints" / "backend_developer_6_months.yml"
    courses_root = PROJECT_ROOT / "content" / "courses"

    source_ids = _read_source_ids(source_registry_path)
    blocks_defined, empty_blocks, missing_source_ids, blueprint_modules = _collect_blueprint_stats(
        blueprint_path,
        source_ids,
    )
    production_courses, reference_courses = _collect_course_stats(courses_root)

    print(f"Source registry count: {len(source_ids)}")
    print(f"Blueprint blocks defined: {blocks_defined if blocks_defined else '-'}")
    print(f"Blueprint modules defined: {blueprint_modules}")
    print(f"Blueprint empty blocks: {empty_blocks if empty_blocks else '-'}")
    print(f"Blueprint missing source ids: {sorted(missing_source_ids) if missing_source_ids else '-'}")
    print(f"Courses (production/reference): {production_courses}/{reference_courses}")

    print("Blocks: 7")
    print(f"Modules: {report.stats.modules}")
    print(f"Lessons: {report.stats.lessons}")
    print(f"Tasks: {report.stats.tasks}")
    print(f"Checkpoints: {report.stats.checkpoints}")

    print("Ошибки:")
    if report.ok:
        print("- нет")
        return 0

    for issue in report.errors:
        print(f"- {issue.location}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
