from getpass import getpass

from sqlmodel import Session, select

from app.db import get_engine, init_db
from app.models import User
from app.security import hash_password


def _prompt_password() -> str:
    password = getpass("Новый пароль: ")
    confirm = getpass("Повторите новый пароль: ")
    if password != confirm:
        raise ValueError("Пароли не совпадают.")
    if not password:
        raise ValueError("Пароль не может быть пустым.")
    return password


def main() -> None:
    username = input("Логин пользователя: ").strip()
    if not username:
        raise ValueError("Логин обязателен.")
    new_password = _prompt_password()

    init_db()
    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise ValueError("Пользователь не найден.")

        user.password_hash = hash_password(new_password)
        session.add(user)
        session.commit()

    print(f"Пароль для '{username}' обновлен.")


if __name__ == "__main__":
    main()
