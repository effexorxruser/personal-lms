from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings


def configure_middleware(app: FastAPI) -> None:
    settings = get_settings()
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret_key,
        session_cookie=settings.session_cookie_name,
        max_age=settings.session_max_age,
        same_site=settings.session_cookie_samesite,
        https_only=settings.session_cookie_secure,
    )
