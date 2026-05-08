from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from fastapi import Request
from starlette.background import BackgroundTask
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from app.config import get_settings

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


class FeatureAwareTemplates(Jinja2Templates):
    """Подмешивает флаги UI из настроек в каждый шаблон."""

    def TemplateResponse(
        self,
        request: Request,
        name: str,
        context: dict[str, Any] | None = None,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> Response:
        merged = dict(context or {})
        settings = get_settings()
        merged.setdefault("feature_ai_helper", settings.enable_ai_helper)
        merged.setdefault("feature_terminal", settings.enable_terminal)
        return super().TemplateResponse(
            request,
            name,
            merged,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )


templates = FeatureAwareTemplates(directory=str(TEMPLATES_DIR))
