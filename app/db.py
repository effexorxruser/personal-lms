from pathlib import Path

from sqlmodel import SQLModel, create_engine

from app.config import get_settings


def _sqlite_connect_args(database_url: str) -> dict[str, bool]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


settings = get_settings()
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=_sqlite_connect_args(settings.database_url),
)


def init_db() -> None:
    if settings.database_url.startswith("sqlite:///./instance/"):
        Path("instance").mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
