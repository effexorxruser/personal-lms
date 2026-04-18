from __future__ import annotations

from enum import StrEnum


class LainHelperMode(StrEnum):
    EXPLAIN_LESSON = "explain_lesson"
    HELP_START = "help_start"
    STUCK_HELP = "stuck_help"
    SUBMISSION_HINT = "submission_hint"
    FREE_QUESTION = "free_question"
