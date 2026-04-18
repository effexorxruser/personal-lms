from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_engine
from app.models import TerminalRun
from app.services.content_service import get_lesson_or_404
from app.services.task_service import resolve_lesson_task
from app.services.terminal_service import get_terminal_history, run_terminal_command

router = APIRouter(prefix="/api/terminal", tags=["terminal"])


class TerminalRunRequest(BaseModel):
    command: str


def _require_user_id(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Требуется вход")
    return int(user_id)


def _serialize_run(run: TerminalRun) -> dict:
    return {
        "id": run.id,
        "lesson_key": run.lesson_key,
        "task_slug": run.task_slug,
        "command_text": run.command_text,
        "normalized_command": run.normalized_command,
        "exit_code": run.exit_code,
        "stdout_text": run.stdout_text,
        "stderr_text": run.stderr_text,
        "status": run.status,
        "duration_ms": run.duration_ms,
        "created_at": run.created_at.isoformat() if isinstance(run.created_at, datetime) else str(run.created_at),
    }


def _terminal_task_or_404(lesson_key: str):
    lesson = get_lesson_or_404(lesson_key)
    task_resolution = resolve_lesson_task(lesson)
    task = task_resolution.task
    if task is None or not task.terminal or not task.terminal.enabled:
        raise HTTPException(status_code=404, detail="Терминал не включён для этого урока")
    return lesson, task


@router.get("/lessons/{lesson_key}/history")
def terminal_history(request: Request, lesson_key: str) -> dict:
    user_id = _require_user_id(request)
    _terminal_task_or_404(lesson_key)
    with Session(get_engine()) as session:
        runs = get_terminal_history(session, user_id, lesson_key)
    return {"runs": [_serialize_run(run) for run in runs]}


@router.post("/lessons/{lesson_key}/run")
def terminal_run(request: Request, lesson_key: str, payload: TerminalRunRequest) -> dict:
    user_id = _require_user_id(request)
    lesson, task = _terminal_task_or_404(lesson_key)
    with Session(get_engine()) as session:
        result = run_terminal_command(
            session=session,
            user_id=user_id,
            lesson=lesson,
            task=task,
            command_text=payload.command,
        )
        session.commit()
        session.refresh(result.run)
        run = result.run
    return {"run": _serialize_run(run)}
