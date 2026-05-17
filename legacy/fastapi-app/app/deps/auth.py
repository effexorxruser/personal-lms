from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.models import User


def redirect_if_anonymous(request: Request) -> RedirectResponse | None:
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=303)
    return None


def load_active_user(session: Session, *, user_id: int) -> User | None:
    user = session.get(User, user_id)
    if user is None or not user.is_active:
        return None
    return user


def ensure_admin_web(request: Request, session: Session) -> RedirectResponse | None:
    """Аноним → редирект на логин; не-admin → исключение 403 для HTML-хендлеров."""
    redir = redirect_if_anonymous(request)
    if redir is not None:
        return redir
    user_id = int(request.session["user_id"])
    user = load_active_user(session, user_id=user_id)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Нужна роль администратора.")
    return None

