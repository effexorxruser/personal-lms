from __future__ import annotations

import argparse
import sys
from getpass import getpass

from sqlmodel import Session, select

from app.db import get_engine, init_db
from app.models import User
from app.security import hash_password


def _prompt_password() -> str:
    password = getpass("Введите пароль: ")
    confirm = getpass("Повторите пароль: ")
    if password != confirm:
        raise ValueError("Пароли не совпадают.")
    if not password:
        raise ValueError("Пароль не может быть пустым.")
    return password


def _interactive_create() -> None:
    username = input("Логин: ").strip()
    display_name = input("Отображаемое имя: ").strip()
    if not username or not display_name:
        raise ValueError("Логин и отображаемое имя обязательны.")
    password = _prompt_password()

    init_db()
    with Session(get_engine()) as session:
        existing = session.exec(select(User).where(User.username == username)).first()
        if existing:
            raise ValueError("Пользователь с таким логином уже существует.")

        user = User(
            username=username,
            display_name=display_name,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        session.add(user)
        session.commit()

    print(f"Пользователь '{username}' (role=admin) создан.")


def _resolve_password(cli_password: str | None) -> str:
    if cli_password:
        if not cli_password.strip():
            raise ValueError("Пароль не может быть пустым.")
        return cli_password
    return _prompt_password()


def main() -> None:
    if len(sys.argv) <= 1:
        _interactive_create()
        return

    parser = argparse.ArgumentParser(description="Создание пользователя personal-lms (CLI режим)")
    parser.add_argument("--username", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument(
        "--password",
        default=None,
        help="Пароль (если не задан — запрос через getpass)",
    )
    parser.add_argument("--role", choices=["admin", "learner"], default="learner")
    parser.set_defaults(is_active=True)
    state_group = parser.add_mutually_exclusive_group()
    state_group.add_argument("--active", dest="is_active", action="store_true", help="Активный пользователь")
    state_group.add_argument("--inactive", dest="is_active", action="store_false", help="Неактивный пользователь")

    args = parser.parse_args()
    username = args.username.strip()
    display_name = args.display_name.strip()
    if not username or not display_name:
        raise ValueError("Логин и отображаемое имя не могут быть пустыми.")

    password = _resolve_password(args.password)

    init_db()
    with Session(get_engine()) as session:
        existing = session.exec(select(User).where(User.username == username)).first()
        if existing:
            raise ValueError("Пользователь с таким логином уже существует.")

        user = User(
            username=username,
            display_name=display_name,
            password_hash=hash_password(password),
            role=args.role,
            is_active=args.is_active,
        )
        session.add(user)
        session.commit()

    state = "active" if args.is_active else "inactive"
    print(f"Пользователь '{username}' (role={args.role}, {state}) создан.")


if __name__ == "__main__":
    main()
