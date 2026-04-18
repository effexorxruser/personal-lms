from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_engine
from app.services.ai_helper_service import LainHelperError, assist_with_lain

router = APIRouter(prefix="/api/ai", tags=["ai-helper"])


class AIHelperRequest(BaseModel):
    lesson_key: str
    mode: str
    message: str = ""
    submission_draft: str | None = None


def _require_user_id(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Требуется вход")
    return int(user_id)


@router.post("/helper")
def ai_helper(request: Request, payload: AIHelperRequest) -> dict:
    user_id = _require_user_id(request)

    with Session(get_engine()) as session:
        try:
            result = assist_with_lain(
                session=session,
                user_id=user_id,
                lesson_key=payload.lesson_key,
                mode=payload.mode,
                user_message=payload.message,
                submission_draft=payload.submission_draft,
            )
        except LainHelperError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        session.commit()

    return {
        "status": result.status,
        "lesson_key": result.lesson_key,
        "mode": result.mode,
        "assistant_message": result.assistant_message,
        "interaction_id": result.interaction_id,
    }
