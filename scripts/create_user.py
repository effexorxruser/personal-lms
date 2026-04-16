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


def main() -> None:
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


if __name__ == "__main__":
    main()
