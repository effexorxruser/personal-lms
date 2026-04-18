from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, field_validator
from sqlmodel import Session

from app.db import get_engine
from app.services.ai_helper_modes import LainHelperMode
from app.services.ai_helper_service import LainHelperError, assist_with_lain, list_lain_history

router = APIRouter(prefix="/api/ai", tags=["ai-helper"])


class AIHelperRequest(BaseModel):
    lesson_key: str
    mode: LainHelperMode
    message: str = ""
    submission_draft: str | None = None

    @field_validator("mode", mode="before")
    @classmethod
    def normalize_mode(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class AIHelperHistoryItem(BaseModel):
    id: int
    lesson_key: str
    mode: LainHelperMode
    user_message: str
    assistant_message: str
    created_at: str


class AIHelperHistoryResponse(BaseModel):
    lesson_key: str | None = None
    items: list[AIHelperHistoryItem]


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
        "mode": result.mode.value,
        "assistant_message": result.assistant_message,
        "interaction_id": result.interaction_id,
    }


@router.get("/helper/history", response_model=AIHelperHistoryResponse)
def ai_helper_history(
    request: Request,
    lesson_key: str | None = None,
    limit: int = Query(default=12, ge=1, le=40),
) -> AIHelperHistoryResponse:
    user_id = _require_user_id(request)
    normalized_lesson_key = lesson_key.strip() if lesson_key and lesson_key.strip() else None

    with Session(get_engine()) as session:
        entries = list_lain_history(
            session=session,
            user_id=user_id,
            lesson_key=normalized_lesson_key,
            limit=limit,
        )

    return AIHelperHistoryResponse(
        lesson_key=normalized_lesson_key,
        items=[
            AIHelperHistoryItem(
                id=item.id,
                lesson_key=item.lesson_key,
                mode=item.mode,
                user_message=item.user_message,
                assistant_message=item.assistant_message,
                created_at=item.created_at.isoformat(),
            )
            for item in entries
        ],
    )
