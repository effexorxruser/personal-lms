"""Общие предпосылки для тестов: флаги до импорта приложения."""

import os

# Терминал по умолчанию включён в тестах, чтобы smoke и интеграционные сценарии
# не ломались при PERSONAL_LMS_ENABLE_TERMINAL=false в production.
os.environ.setdefault("PERSONAL_LMS_ENABLE_TERMINAL", "true")
