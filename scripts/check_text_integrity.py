#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INCLUDE_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
    ".html",
    ".css",
    ".js",
    ".sql",
    ".env",
}

EXCLUDE_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "instance",
}

MOJIBAKE_MARKERS = (
    "\u00C3",
    "\u00D0",
    "\u00D1",
    "\u00E2\u20AC",
    "\u00EF\u00BB\u00BF",
    "\uFFFD",
)


def should_check(path: Path) -> bool:
    if any(part in EXCLUDE_PARTS for part in path.parts):
        return False
    if path.name == ".env":
        return True
    return path.suffix.lower() in INCLUDE_SUFFIXES


def main() -> int:
    issues: list[str] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not should_check(path):
            continue

        rel_path = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            issues.append(f"{rel_path}: invalid UTF-8 ({exc})")
            continue

        for marker in MOJIBAKE_MARKERS:
            if marker in text:
                issues.append(f"{rel_path}: possible mojibake marker U+{ord(marker[0]):04X}")
                break

    if issues:
        print("Text integrity check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Text integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
