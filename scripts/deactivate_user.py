from __future__ import annotations

import argparse

from sqlmodel import Session, select

from app.db import get_engine, init_db
from app.models import User


def main() -> None:
    parser = argparse.ArgumentParser(description="Деактивация пользователя (is_active=false, без удаления)")
    parser.add_argument("--username", required=True)
    args = parser.parse_args()
    username = args.username.strip()
    if not username:
        raise ValueError("Логин не может быть пустым.")

    init_db()
    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise ValueError(f"Пользователь '{username}' не найден.")
        user.is_active = False
        session.add(user)
        session.commit()

    print(f"Пользователь '{username}' помечен неактивным.")


if __name__ == "__main__":
    main()
