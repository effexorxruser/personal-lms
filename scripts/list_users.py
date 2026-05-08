from __future__ import annotations

from sqlmodel import Session, select

from app.db import get_engine, init_db
from app.models import User


def main() -> None:
    init_db()
    with Session(get_engine()) as session:
        users = sorted(session.exec(select(User)).all(), key=lambda u: u.username)

    rows = [["username", "display_name", "role", "is_active", "created_at"]]
    for user in users:
        created = user.created_at.isoformat() if user.created_at else ""
        rows.append(
            [
                user.username,
                user.display_name,
                user.role,
                str(user.is_active),
                created,
            ],
        )

    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    for row in rows:
        line = "  ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
        print(line)


if __name__ == "__main__":
    main()
