"""Детерминированные ключи и копирайт для tests/fixtures/content_pack."""

from pathlib import Path

CONTENT_PACK_ROOT = Path(__file__).resolve().parent / "fixtures" / "content_pack"

ACTIVE_COURSE_SLUG = "test-python-course"
DRAFT_MODULE_COURSE_SLUG = "test-draft-module-course"

# Block 0 equivalent (available course)
L_B0_WS = "test-b0-workspace-baseline"
L_B0_CLI = "test-b0-python-cli-smoke"
L_B0_GIT = "test-b0-git-github-cycle"
L_B0_LOOP = "test-b0-learning-loop-setup"
L_B0_LOG = "test-b0-study-log-baseline"

CP_B0_WS = "test-b0-workspace-checkpoint"
CP_B0_LEARN = "test-b0-learning-checkpoint"

# Foundation equivalent (draft course)
L_FND_WS = "test-fnd-workspace"
L_FND_CLI = "test-fnd-cli-python"
L_FND_GIT = "test-fnd-git-loop"
CP_FND_START = "test-fnd-start-pack"

TASK_FND_CLI = "test-fnd-task-cli-smoke"

TITLE_B0_WS = "Урок 0.1: Подготовка учебного workspace"
TITLE_B0_CLI = "Урок 0.2: Первый Python CLI smoke cycle"
TITLE_B0_GIT = "Урок 0.3: Базовый Git/GitHub cycle"
TITLE_B0_LOOP = "Урок 0.4: Weekly learning loop setup"
TITLE_B0_LOG = "Урок 0.5: Базовый учебный журнал"

TITLE_FND_WS = "Урок 1: Рабочее место и стартовый ритм"
TITLE_FND_CLI = "Урок 2: Базовый Python execution loop"

TASK_TITLE_CLI_SMOKE = "Собрать и прогнать hello CLI script"

AVAILABLE_COURSE_CATALOG_TITLE = "Catalog Test Course"
DRAFT_COURSE_TITLE = "Draft Hidden From Catalog"

COURSE_FACTORY_LEAK_MARKER = "Course Factory Reference Fixtures"
