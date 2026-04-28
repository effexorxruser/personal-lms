from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Callable

import httpx
import yaml

from app.content_pipeline import PROJECT_ROOT, SOURCE_ROOT, SourceRegistryEntrySchema, _BuildState, _read_source_registry

DEFAULT_TIMEOUT_SECONDS = 15.0
DEFAULT_MAX_RESPONSE_BYTES = 2_000_000
DEFAULT_USER_AGENT = "personal-lms-source-fetcher/1.0"
CACHE_ROOT = PROJECT_ROOT / "var" / "source_cache"
MANIFEST_PATH = CACHE_ROOT / "manifest.yml"


class SourceFetcherError(ValueError):
    """Base exception for source fetch/cache operations."""


class SourceNotFoundError(SourceFetcherError):
    """Raised when source_id is absent in approved source registry."""


@dataclass(frozen=True)
class WebFetchResult:
    status_code: int
    body_text: str
    content_length: int


@dataclass(frozen=True)
class SourceFetchRun:
    run_id: str
    source_id: str
    url: str
    retrieval_mode: str
    status: str
    http_status: int | None
    content_hash: str | None
    snapshot_path: str | None
    fetched_at: str
    content_length: int
    error: str | None


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_registry(source_root: Path = SOURCE_ROOT) -> dict[str, SourceRegistryEntrySchema]:
    state = _BuildState()
    entries = _read_source_registry(source_root, state)
    if state.errors:
        details = "; ".join(f"{item.location}: {item.message}" for item in state.errors)
        raise SourceFetcherError(f"source registry validation failed: {details}")
    return entries


def get_source_by_id(source_id: str, source_root: Path = SOURCE_ROOT) -> SourceRegistryEntrySchema:
    registry = _load_registry(source_root=source_root)
    source = registry.get(source_id)
    if source is None:
        raise SourceNotFoundError(f"unknown source_id: {source_id}")
    return source


def list_source_ids(source_root: Path = SOURCE_ROOT) -> list[str]:
    return sorted(_load_registry(source_root=source_root).keys())


def list_sources(source_root: Path = SOURCE_ROOT) -> dict[str, SourceRegistryEntrySchema]:
    return _load_registry(source_root=source_root)


def fetch_web_text(
    *,
    url: str,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
    user_agent: str = DEFAULT_USER_AGENT,
) -> WebFetchResult:
    with httpx.Client(
        timeout=timeout_seconds,
        headers={"User-Agent": user_agent},
        follow_redirects=True,
    ) as client:
        with client.stream("GET", url) as response:
            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_bytes():
                total += len(chunk)
                if total > max_response_bytes:
                    raise SourceFetcherError(
                        f"response too large for {url}: {total} bytes exceeds limit {max_response_bytes}"
                    )
                chunks.append(chunk)
            body = b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")
            return WebFetchResult(
                status_code=response.status_code,
                body_text=body,
                content_length=total,
            )


def _safe_snapshot_dir(cache_root: Path, source_id: str) -> Path:
    base = cache_root.resolve()
    target = (cache_root / "snapshots" / source_id).resolve()
    if base not in [target, *target.parents]:
        raise SourceFetcherError(f"unsafe snapshot path resolved for source_id={source_id}")
    target.mkdir(parents=True, exist_ok=True)
    return target


def _write_snapshot(*, cache_root: Path, source_id: str, body_text: str) -> tuple[str, str, int]:
    encoded = body_text.encode("utf-8")
    content_hash = sha256(encoded).hexdigest()
    snapshot_dir = _safe_snapshot_dir(cache_root, source_id)
    snapshot_path = snapshot_dir / f"{content_hash}.txt"
    snapshot_path.write_text(body_text, encoding="utf-8")
    relative_path = snapshot_path.relative_to(cache_root).as_posix()
    return content_hash, relative_path, len(encoded)


def _append_manifest(cache_root: Path, runs: list[SourceFetchRun]) -> None:
    cache_root.mkdir(parents=True, exist_ok=True)
    manifest_path = cache_root / "manifest.yml"
    payload: dict[str, list[dict]]
    if manifest_path.exists():
        loaded = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict) or not isinstance(loaded.get("runs"), list):
            payload = {"runs": []}
        else:
            payload = {"runs": list(loaded["runs"])}
    else:
        payload = {"runs": []}
    payload["runs"].extend(asdict(item) for item in runs)
    manifest_path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _urls_for_fetch(source: SourceRegistryEntrySchema, section: str) -> list[str]:
    urls: list[str] = []
    if section == "all":
        urls.append(source.canonical_url)
        urls.extend(source.retrieval.preferred_sections)
    else:
        urls.append(source.canonical_url)
    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped


def fetch_source(
    *,
    source_id: str,
    section: str = "canonical",
    source_root: Path = SOURCE_ROOT,
    cache_root: Path = CACHE_ROOT,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
    user_agent: str = DEFAULT_USER_AGENT,
    fetch_web: Callable[..., WebFetchResult] = fetch_web_text,
) -> list[SourceFetchRun]:
    source = get_source_by_id(source_id, source_root=source_root)
    mode = source.retrieval.mode
    run_id = _now_iso()
    fetched_at = _now_iso()
    runs: list[SourceFetchRun] = []

    if mode == "disabled":
        runs.append(
            SourceFetchRun(
                run_id=run_id,
                source_id=source.id,
                url=source.canonical_url,
                retrieval_mode=mode,
                status="disabled",
                http_status=None,
                content_hash=None,
                snapshot_path=None,
                fetched_at=fetched_at,
                content_length=0,
                error="source retrieval is disabled",
            )
        )
        _append_manifest(cache_root, runs)
        return runs

    if mode == "manual":
        runs.append(
            SourceFetchRun(
                run_id=run_id,
                source_id=source.id,
                url=source.canonical_url,
                retrieval_mode=mode,
                status="manual_required",
                http_status=None,
                content_hash=None,
                snapshot_path=None,
                fetched_at=fetched_at,
                content_length=0,
                error="manual retrieval required",
            )
        )
        _append_manifest(cache_root, runs)
        return runs

    if mode == "mcp":
        runs.append(
            SourceFetchRun(
                run_id=run_id,
                source_id=source.id,
                url=source.canonical_url,
                retrieval_mode=mode,
                status="unsupported_mode",
                http_status=None,
                content_hash=None,
                snapshot_path=None,
                fetched_at=fetched_at,
                content_length=0,
                error="mcp mode is not implemented in v1 fetcher",
            )
        )
        _append_manifest(cache_root, runs)
        return runs

    if mode != "web":
        runs.append(
            SourceFetchRun(
                run_id=run_id,
                source_id=source.id,
                url=source.canonical_url,
                retrieval_mode=mode,
                status="unsupported_mode",
                http_status=None,
                content_hash=None,
                snapshot_path=None,
                fetched_at=fetched_at,
                content_length=0,
                error=f"unsupported retrieval mode: {mode}",
            )
        )
        _append_manifest(cache_root, runs)
        return runs

    for url in _urls_for_fetch(source, section):
        try:
            result = fetch_web(
                url=url,
                timeout_seconds=timeout_seconds,
                max_response_bytes=max_response_bytes,
                user_agent=user_agent,
            )
        except Exception as exc:
            runs.append(
                SourceFetchRun(
                    run_id=run_id,
                    source_id=source.id,
                    url=url,
                    retrieval_mode=mode,
                    status="error",
                    http_status=None,
                    content_hash=None,
                    snapshot_path=None,
                    fetched_at=fetched_at,
                    content_length=0,
                    error=str(exc),
                )
            )
            continue

        if 200 <= result.status_code < 300:
            content_hash, snapshot_path, content_length = _write_snapshot(
                cache_root=cache_root,
                source_id=source.id,
                body_text=result.body_text,
            )
            runs.append(
                SourceFetchRun(
                    run_id=run_id,
                    source_id=source.id,
                    url=url,
                    retrieval_mode=mode,
                    status="ok",
                    http_status=result.status_code,
                    content_hash=content_hash,
                    snapshot_path=snapshot_path,
                    fetched_at=fetched_at,
                    content_length=content_length,
                    error=None,
                )
            )
        else:
            runs.append(
                SourceFetchRun(
                    run_id=run_id,
                    source_id=source.id,
                    url=url,
                    retrieval_mode=mode,
                    status="error",
                    http_status=result.status_code,
                    content_hash=None,
                    snapshot_path=None,
                    fetched_at=fetched_at,
                    content_length=result.content_length,
                    error=f"http status {result.status_code}",
                )
            )

    _append_manifest(cache_root, runs)
    return runs
