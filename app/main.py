from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.middleware import configure_middleware
from app.routers.auth import router as auth_router
from app.routers.ai_helper import router as ai_helper_router
from app.routers.content import router as content_router
from app.routers.dashboard import router as dashboard_router
from app.routers.terminal import router as terminal_router

BASE_DIR = Path(__file__).resolve().parent


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, debug=settings.debug)

    application.mount(
        "/static",
        StaticFiles(directory=BASE_DIR / "static"),
        name="static",
    )
    application.mount(
        "/assets",
        StaticFiles(directory=BASE_DIR.parent / "assets"),
        name="assets",
    )
    configure_middleware(application)
    application.include_router(auth_router)
    application.include_router(ai_helper_router)
    application.include_router(content_router)
    application.include_router(dashboard_router)
    application.include_router(terminal_router)

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/", include_in_schema=False)
    def index() -> RedirectResponse:
        return RedirectResponse(url="/dashboard")

    return application


app = create_app()
