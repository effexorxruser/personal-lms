#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.source_fetcher import CACHE_ROOT, SOURCE_ROOT, SourceFetcherError, fetch_source, get_source_by_id, list_source_ids


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch approved source(s) into local source cache.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--source-id", help="Single source id from content/sources/source_registry.yml")
    target.add_argument("--all", action="store_true", help="Fetch all approved sources from source registry")
    parser.add_argument(
        "--section",
        choices=["canonical", "all"],
        default="canonical",
        help="canonical: canonical_url only; all: canonical_url + preferred_sections",
    )
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT, help="Path to source registry directory")
    parser.add_argument("--cache-root", type=Path, default=CACHE_ROOT, help="Path to local source cache")
    args = parser.parse_args()

    source_ids: list[str]
    if args.source_id:
        source_ids = [args.source_id]
    else:
        source_ids = list_source_ids(source_root=args.source_root)

    any_errors = False
    for source_id in source_ids:
        try:
            source = get_source_by_id(source_id, source_root=args.source_root)
            runs = fetch_source(
                source_id=source_id,
                section=args.section,
                source_root=args.source_root,
                cache_root=args.cache_root,
            )
            print(f"source_id={source.id} mode={source.retrieval.mode} runs={len(runs)}")
            for run in runs:
                print(
                    f"- status={run.status} url={run.url} "
                    f"http_status={run.http_status} snapshot={run.snapshot_path} error={run.error}"
                )
        except SourceFetcherError as exc:
            any_errors = True
            print(f"source_id={source_id}: error: {exc}")

    return 1 if any_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
