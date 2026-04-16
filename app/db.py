from pathlib import Path
from functools import lru_cache

from sqlmodel import SQLModel, create_engine

from app.config import get_settings


def _ensure_sqlite_url(database_url: str) -> None:
    if not database_url.startswith("sqlite"):
        raise ValueError("Phase 2 supports only SQLite database URLs.")


@lru_cache
def get_engine():
    settings = get_settings()
    _ensure_sqlite_url(settings.database_url)
    return create_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
    )


def init_db() -> None:
    from app import models  # noqa: F401

    settings = get_settings()
    _ensure_sqlite_url(settings.database_url)
    if settings.database_url.startswith("sqlite:///./instance/"):
        Path("instance").mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(get_engine())
