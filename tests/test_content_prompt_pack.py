from __future__ import annotations

from pathlib import Path

import yaml

from scripts.build_content_prompt_pack import PromptPackBuildError, build_prompt_pack


def test_build_prompt_pack_creates_expected_files(tmp_path: Path) -> None:
    output_root = tmp_path / "content_drafts"
    pack_dir = build_prompt_pack(
        block=1,
        module_slug="block-1-python-core",
        output_root=output_root,
        cache_manifest_path=None,
    )

    assert pack_dir.exists()
    assert (pack_dir / "prompt_pack.yml").exists()
    assert (pack_dir / "prompts" / "build_lesson.md").exists()
    assert (pack_dir / "prompts" / "build_task.md").exists()
    assert (pack_dir / "rules" / "russian_friendly.md").exists()
    assert (pack_dir / "schemas" / "draft_output_contract.yml").exists()


def test_prompt_pack_includes_required_lesson_sections(tmp_path: Path) -> None:
    pack_dir = build_prompt_pack(
        block=1,
        module_slug="block-1-python-core",
        output_root=tmp_path / "content_drafts",
        cache_manifest_path=None,
    )
    payload = yaml.safe_load((pack_dir / "prompt_pack.yml").read_text(encoding="utf-8"))

    sections = payload["inputs"]["required_lesson_sections"]
    assert "Why this matters (RU)" in sections
    assert "What to read (EN source)" in sections
    assert "Definition of Done" in sections

    kb_sections = payload["inputs"]["draft_output_contract"]["lesson"]["knowledge_base_required_sections"]
    assert "Core idea (RU)" in kb_sections
    assert "Runnable example" in kb_sections
    assert "Частые ошибки" in kb_sections


def test_build_prompt_pack_fails_for_unknown_module(tmp_path: Path) -> None:
    try:
        build_prompt_pack(
            block=1,
            module_slug="unknown-module",
            output_root=tmp_path / "content_drafts",
            cache_manifest_path=None,
        )
    except PromptPackBuildError as exc:
        assert "module not found" in str(exc)
    else:
        raise AssertionError("expected PromptPackBuildError for unknown module")


def test_build_prompt_pack_reads_optional_cache_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "runs": [
                    {
                        "run_id": "r1",
                        "source_id": "python-docs",
                        "status": "ok",
                    }
                ]
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    pack_dir = build_prompt_pack(
        block=1,
        module_slug="block-1-python-core",
        output_root=tmp_path / "content_drafts",
        cache_manifest_path=manifest,
    )

    payload = yaml.safe_load((pack_dir / "prompt_pack.yml").read_text(encoding="utf-8"))
    latest = payload["inputs"]["source_cache_latest"]
    assert "python-docs" in latest
    assert latest["python-docs"]["run_id"] == "r1"


def test_build_lesson_prompt_contains_knowledge_unit_requirements(tmp_path: Path) -> None:
    pack_dir = build_prompt_pack(
        block=1,
        module_slug="block-1-python-core",
        output_root=tmp_path / "content_drafts",
        cache_manifest_path=None,
    )
    prompt_text = (pack_dir / "prompts" / "build_lesson.md").read_text(encoding="utf-8")

    assert "standalone knowledge unit" in prompt_text
    assert "## Core idea (RU)" in prompt_text
    assert "## Runnable example" in prompt_text
    assert "## Run and expected output" in prompt_text
    assert "## Частые ошибки" in prompt_text
    assert "## Как это связано с задачей" in prompt_text
    assert "optional deep-dive" in prompt_text
    assert "tiny example -> explanation -> slightly larger example -> task bridge" in prompt_text
    assert "do not use type hints in the first explanation example" in prompt_text
    assert "Markdown code fences must be valid" in prompt_text


def test_validate_prompt_enforces_no_manual_hunting_policy(tmp_path: Path) -> None:
    pack_dir = build_prompt_pack(
        block=1,
        module_slug="block-1-python-core",
        output_root=tmp_path / "content_drafts",
        cache_manifest_path=None,
    )
    validate_text = (pack_dir / "prompts" / "validate_draft.md").read_text(encoding="utf-8")

    assert "No instruction that forces manual source hunting." in validate_text
    assert "`What to read (EN source)` is optional deep dive" in validate_text
    assert "Markdown fences in lesson code blocks are valid and renderable." in validate_text


def test_draft_output_contract_includes_beginner_and_markdown_policies(tmp_path: Path) -> None:
    pack_dir = build_prompt_pack(
        block=1,
        module_slug="block-1-python-core",
        output_root=tmp_path / "content_drafts",
        cache_manifest_path=None,
    )
    payload = yaml.safe_load((pack_dir / "prompt_pack.yml").read_text(encoding="utf-8"))
    lesson_contract = payload["inputs"]["draft_output_contract"]["lesson"]

    assert lesson_contract["micro_step_policy"]["early_modules_first_example_minimal"] is True
    assert lesson_contract["micro_step_policy"]["early_modules_no_type_hints_in_first_example"] is True
    assert lesson_contract["markdown_code_fence_policy"]["opening_fence_has_language_marker"] is True
