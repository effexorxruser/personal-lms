from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.db import get_engine
from app.services.ai_helper_service import (
    clear_history,
    create_chat_turn,
    get_history,
    is_helper_online,
    resolve_helper_context,
    serialize_message,
)

router = APIRouter(prefix="/api/ai-helper", tags=["ai-helper"])


class HelperChatRequest(BaseModel):
    path: str = Field(default="/dashboard")
    message: str = Field(min_length=1, max_length=2000)
    socratic_mode: bool = False


class HelperContextRequest(BaseModel):
    path: str = Field(default="/dashboard")


def _require_user_id(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Требуется вход")
    return int(user_id)


@router.post("/history")
def ai_helper_history(request: Request, payload: HelperContextRequest) -> dict:
    user_id = _require_user_id(request)
    context = resolve_helper_context(payload.path)
    with Session(get_engine()) as session:
        rows = get_history(session, user_id, context.key)
    return {
        "context_key": context.key,
        "context_label": context.label,
        "online": is_helper_online(),
        "messages": [serialize_message(row) for row in rows],
    }


@router.post("/chat")
def ai_helper_chat(request: Request, payload: HelperChatRequest) -> dict:
    user_id = _require_user_id(request)
    context = resolve_helper_context(payload.path)
    with Session(get_engine()) as session:
        user_row, assistant_row = create_chat_turn(
            session,
            user_id=user_id,
            context=context,
            user_message=payload.message,
            socratic_mode=payload.socratic_mode,
        )
        session.commit()
        session.refresh(user_row)
        session.refresh(assistant_row)
        serialized_messages = [serialize_message(user_row), serialize_message(assistant_row)]
    return {
        "context_key": context.key,
        "context_label": context.label,
        "online": is_helper_online(),
        "messages": serialized_messages,
    }


@router.post("/clear")
def ai_helper_clear(request: Request, payload: HelperContextRequest) -> dict:
    user_id = _require_user_id(request)
    context = resolve_helper_context(payload.path)
    with Session(get_engine()) as session:
        clear_history(session, user_id, context.key)
        session.commit()
    return {"ok": True, "context_key": context.key, "context_label": context.label}
