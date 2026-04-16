from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings


def configure_middleware(app: FastAPI) -> None:
    settings = get_settings()
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret_key,
        same_site="lax",
        https_only=False,
    )
