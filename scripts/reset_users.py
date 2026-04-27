import argparse

from sqlmodel import Session

from app.db import get_engine, init_db


DELETE_STATEMENTS = (
    "DELETE FROM lainhelperinteraction;",
    "DELETE FROM terminalrun;",
    "DELETE FROM stuckevent;",
    "DELETE FROM checkpointreview;",
    "DELETE FROM checkpointsubmission;",
    "DELETE FROM reviewresult;",
    "DELETE FROM tasksubmission;",
    "DELETE FROM lessonprogress;",
    "DELETE FROM courseprogress;",
    "DELETE FROM user;",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Удаляет всех пользователей и связанный runtime state из локальной SQLite БД."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Пропустить подтверждение и выполнить удаление сразу.",
    )
    return parser.parse_args()


def _confirm(force: bool) -> bool:
    if force:
        return True

    answer = input(
        "Это удалит ВСЕХ пользователей и их runtime-данные. Продолжить? [y/N]: "
    ).strip()
    return answer.lower() in {"y", "yes"}


def main() -> None:
    args = _parse_args()
    if not _confirm(args.yes):
        print("Отменено.")
        return

    init_db()
    with Session(get_engine()) as session:
        connection = session.connection()
        for statement in DELETE_STATEMENTS:
            connection.exec_driver_sql(statement)
        session.commit()

    print("Все пользователи и связанные runtime-данные удалены.")


if __name__ == "__main__":
    main()
