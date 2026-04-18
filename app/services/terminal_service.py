from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import shlex
import subprocess
import sys
import time

from sqlmodel import Session, select

from app.content_loader import LessonContent, TaskContent
from app.models import TerminalRun

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INSTANCE_ROOT = PROJECT_ROOT / "instance" / "terminal"
MAX_OUTPUT_CHARS = 12_000
DEFAULT_TIMEOUT_SECONDS = 1


@dataclass(frozen=True)
class TerminalCommandResult:
    run: TerminalRun
    blocked_reason: str | None = None


class TerminalCommandError(ValueError):
    pass


def lesson_sandbox_dir(user_id: int, lesson_key: str) -> Path:
    safe_lesson_key = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in lesson_key)
    return INSTANCE_ROOT / str(user_id) / safe_lesson_key


def _trim_output(value: str) -> str:
    if len(value) <= MAX_OUTPUT_CHARS:
        return value
    return value[:MAX_OUTPUT_CHARS] + "\n... output truncated ..."


def _safe_relative_path(raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute() or any(part == ".." for part in candidate.parts):
        raise TerminalCommandError("Путь должен быть относительным и оставаться внутри sandbox урока.")
    if not candidate.parts:
        raise TerminalCommandError("Не указан относительный путь к файлу.")
    return candidate


def _ensure_lesson_file(sandbox_dir: Path, lesson: LessonContent) -> Path:
    lesson_file = sandbox_dir / "lesson.py"
    if not lesson_file.exists():
        lesson_file.write_text(
            "print('lesson sandbox ready')\n"
            f"print('lesson: {lesson.key}')\n",
            encoding="utf-8",
        )
    return lesson_file


def _tree(sandbox_dir: Path) -> str:
    entries: list[str] = ["."]
    for path in sorted(sandbox_dir.rglob("*")):
        if path == sandbox_dir:
            continue
        relative = path.relative_to(sandbox_dir)
        if len(relative.parts) > 4:
            continue
        prefix = "  " * (len(relative.parts) - 1)
        suffix = "/" if path.is_dir() else ""
        entries.append(f"{prefix}{relative.name}{suffix}")
    return "\n".join(entries)


def _task_text(task: TaskContent) -> str:
    done = "\n".join(f"- {item}" for item in task.definition_of_done)
    hints = "\n".join(f"- {item}" for item in task.hints)
    return (
        f"{task.title}\n\n"
        f"{task.summary}\n\n"
        f"Инструкция:\n{task.instructions}\n\n"
        f"Критерии готовности:\n{done}"
        + (f"\n\nПодсказки:\n{hints}" if hints else "")
    )


def _done_text(task: TaskContent) -> str:
    return "\n".join(f"- {item}" for item in task.definition_of_done)


def _help_text(task: TaskContent) -> str:
    configured = ", ".join(task.terminal.allowed_commands) if task.terminal else "help, pwd, tree, python, pytest, show"
    return (
        "Доступные команды учебного терминала:\n"
        "- help\n"
        "- pwd\n"
        "- tree\n"
        "- python --version\n"
        "- python run lesson\n"
        "- python run file <relative_path>\n"
        "- pytest lesson\n"
        "- show task\n"
        "- show done\n\n"
        f"Разрешённые группы для этой задачи: {configured}"
    )


def _blocked_run(
    session: Session,
    user_id: int,
    lesson: LessonContent,
    task: TaskContent,
    command_text: str,
    normalized_command: str,
    reason: str,
) -> TerminalCommandResult:
    run = TerminalRun(
        user_id=user_id,
        lesson_key=lesson.key,
        task_slug=task.slug,
        command_text=command_text,
        normalized_command=normalized_command,
        exit_code=None,
        stdout_text="",
        stderr_text=reason,
        status="blocked",
        duration_ms=0,
    )
    session.add(run)
    session.flush()
    return TerminalCommandResult(run=run, blocked_reason=reason)


def _completed_internal_run(
    session: Session,
    user_id: int,
    lesson: LessonContent,
    task: TaskContent,
    command_text: str,
    normalized_command: str,
    stdout_text: str,
) -> TerminalCommandResult:
    run = TerminalRun(
        user_id=user_id,
        lesson_key=lesson.key,
        task_slug=task.slug,
        command_text=command_text,
        normalized_command=normalized_command,
        exit_code=0,
        stdout_text=_trim_output(stdout_text),
        stderr_text="",
        status="completed",
        duration_ms=0,
    )
    session.add(run)
    session.flush()
    return TerminalCommandResult(run=run)


def _subprocess_run(
    session: Session,
    user_id: int,
    lesson: LessonContent,
    task: TaskContent,
    command_text: str,
    normalized_command: str,
    argv: list[str],
    sandbox_dir: Path,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> TerminalCommandResult:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            argv,
            cwd=sandbox_dir,
            shell=False,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        run = TerminalRun(
            user_id=user_id,
            lesson_key=lesson.key,
            task_slug=task.slug,
            command_text=command_text,
            normalized_command=normalized_command,
            exit_code=completed.returncode,
            stdout_text=_trim_output(completed.stdout),
            stderr_text=_trim_output(completed.stderr),
            status="completed",
            duration_ms=duration_ms,
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        run = TerminalRun(
            user_id=user_id,
            lesson_key=lesson.key,
            task_slug=task.slug,
            command_text=command_text,
            normalized_command=normalized_command,
            exit_code=None,
            stdout_text=_trim_output(exc.stdout or ""),
            stderr_text="Команда остановлена по timeout.",
            status="timeout",
            duration_ms=duration_ms,
        )
    except OSError as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        run = TerminalRun(
            user_id=user_id,
            lesson_key=lesson.key,
            task_slug=task.slug,
            command_text=command_text,
            normalized_command=normalized_command,
            exit_code=None,
            stdout_text="",
            stderr_text=f"Не удалось запустить команду: {exc}",
            status="failed",
            duration_ms=duration_ms,
        )

    session.add(run)
    session.flush()
    return TerminalCommandResult(run=run)


def _normalize_tokens(command_text: str) -> tuple[list[str], str]:
    try:
        tokens = shlex.split(command_text.strip())
    except ValueError as exc:
        raise TerminalCommandError("Команда не распознана.") from exc
    if not tokens:
        raise TerminalCommandError("Команда пустая.")
    return tokens, " ".join(tokens)


def run_terminal_command(
    session: Session,
    user_id: int,
    lesson: LessonContent,
    task: TaskContent,
    command_text: str,
) -> TerminalCommandResult:
    if not task.terminal or not task.terminal.enabled:
        raise TerminalCommandError("Терминал не включён для этой задачи.")

    try:
        tokens, normalized = _normalize_tokens(command_text)
    except TerminalCommandError as exc:
        return _blocked_run(session, user_id, lesson, task, command_text, command_text.strip(), str(exc))

    root_command = tokens[0]
    if root_command not in set(task.terminal.allowed_commands):
        return _blocked_run(
            session,
            user_id,
            lesson,
            task,
            command_text,
            normalized,
            "Команда не разрешена для этого урока.",
        )

    sandbox_dir = lesson_sandbox_dir(user_id, lesson.key)
    sandbox_dir.mkdir(parents=True, exist_ok=True)

    try:
        if tokens == ["help"]:
            return _completed_internal_run(session, user_id, lesson, task, command_text, normalized, _help_text(task))
        if tokens == ["pwd"]:
            return _completed_internal_run(session, user_id, lesson, task, command_text, normalized, str(sandbox_dir))
        if tokens == ["tree"]:
            _ensure_lesson_file(sandbox_dir, lesson)
            return _completed_internal_run(session, user_id, lesson, task, command_text, normalized, _tree(sandbox_dir))
        if tokens == ["show", "task"]:
            return _completed_internal_run(session, user_id, lesson, task, command_text, normalized, _task_text(task))
        if tokens == ["show", "done"]:
            return _completed_internal_run(session, user_id, lesson, task, command_text, normalized, _done_text(task))
        if tokens == ["python", "--version"]:
            return _subprocess_run(session, user_id, lesson, task, command_text, normalized, [sys.executable, "--version"], sandbox_dir)
        if tokens == ["python", "run", "lesson"]:
            lesson_file = _ensure_lesson_file(sandbox_dir, lesson)
            return _subprocess_run(session, user_id, lesson, task, command_text, normalized, [sys.executable, str(lesson_file)], sandbox_dir)
        if len(tokens) == 4 and tokens[:3] == ["python", "run", "file"]:
            relative_path = _safe_relative_path(tokens[3])
            target = (sandbox_dir / relative_path).resolve()
            if not target.is_relative_to(sandbox_dir.resolve()):
                raise TerminalCommandError("Путь выходит за sandbox урока.")
            if not target.exists() or not target.is_file():
                raise TerminalCommandError("Файл не найден внутри sandbox урока.")
            return _subprocess_run(session, user_id, lesson, task, command_text, normalized, [sys.executable, str(target)], sandbox_dir)
        if tokens == ["pytest", "lesson"]:
            tests_dir = sandbox_dir / "tests"
            test_file = sandbox_dir / "test_lesson.py"
            if not tests_dir.exists() and not test_file.exists():
                return _completed_internal_run(
                    session,
                    user_id,
                    lesson,
                    task,
                    command_text,
                    normalized,
                    "Тесты урока пока не добавлены в sandbox.",
                )
            return _subprocess_run(session, user_id, lesson, task, command_text, normalized, [sys.executable, "-m", "pytest", "-q"], sandbox_dir)
    except TerminalCommandError as exc:
        return _blocked_run(session, user_id, lesson, task, command_text, normalized, str(exc))

    return _blocked_run(
        session,
        user_id,
        lesson,
        task,
        command_text,
        normalized,
        "Форма команды не входит в MVP grammar.",
    )


def get_terminal_history(session: Session, user_id: int, lesson_key: str, limit: int = 20) -> list[TerminalRun]:
    return list(
        session.exec(
            select(TerminalRun)
            .where(TerminalRun.user_id == user_id, TerminalRun.lesson_key == lesson_key)
            .order_by(TerminalRun.created_at.desc())
            .limit(limit)
        )
    )
