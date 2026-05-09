#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _rel_files(root: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(root).as_posix()
        out[rel] = path.stat().st_size
    return out


def _top_level_course_yml_keys(root: Path) -> dict[str, set[str]]:
    keys: dict[str, set[str]] = {}
    for course_yml in sorted(root.glob("courses/*/course.yml")):
        rel = course_yml.relative_to(root).as_posix()
        try:
            data = yaml.safe_load(course_yml.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            keys[rel] = set()
            continue
        if isinstance(data, dict):
            keys[rel] = set(data.keys())
        else:
            keys[rel] = set()
    return keys


def main() -> int:
    parser = argparse.ArgumentParser(description="Простое сравнение двух корней course pack (инвентарь + top keys course.yml).")
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    args = parser.parse_args()
    left = args.left.resolve()
    right = args.right.resolve()

    fl = _rel_files(left)
    fr = _rel_files(right)
    only_left = sorted(set(fl) - set(fr))
    only_right = sorted(set(fr) - set(fl))
    both = sorted(set(fl) & set(fr))

    print("Course pack diff")
    print("================")
    print(f"Left:  {left}")
    print(f"Right: {right}")
    print("")
    print(f"Только в left ({len(only_left)}):")
    for name in only_left[:200]:
        print(f"  {name}  ({fl[name]} bytes)")
    if len(only_left) > 200:
        print(f"  ... ещё {len(only_left) - 200}")
    print("")
    print(f"Только в right ({len(only_right)}):")
    for name in only_right[:200]:
        print(f"  {name}  ({fr[name]} bytes)")
    if len(only_right) > 200:
        print(f"  ... ещё {len(only_right) - 200}")
    print("")
    print("Размеры (отличаются):")
    for name in both:
        if fl[name] != fr[name]:
            print(f"  {name}: {fl[name]} -> {fr[name]}")
    print("")
    print("course.yml: отличия по top-level ключам")
    kl = _top_level_course_yml_keys(left)
    kr = _top_level_course_yml_keys(right)
    all_rels = sorted(set(kl) | set(kr))
    for rel in all_rels:
        a, b = kl.get(rel, set()), kr.get(rel, set())
        if a != b:
            print(f"  {rel}")
            print(f"    only left:  {sorted(a - b)}")
            print(f"    only right: {sorted(b - a)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
