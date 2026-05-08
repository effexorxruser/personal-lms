# Конфигурация окружения

Переменные читаются через `pydantic-settings` с префиксом **`PERSONAL_LMS_`** (см. `app/config.py`). Дополнительно поддерживаются **алиасы без префикса** для ключей из ТЗ (перечислены в таблице).

Файл `.env` в корне проекта загружается автоматически, если файл существует.

## Обязательные для надёжного production

| Назначение | Переменная (prefixed) | Рекомендация |
|------------|-----------------------|---------------|
| Секрет сессии | `PERSONAL_LMS_SESSION_SECRET_KEY` | Случайная строка **не короче 32 символов**, не использовать дефолт `change-me-in-env`. |
| Режим отладки | `PERSONAL_LMS_DEBUG` | **`false`** в production. |

## База и приложение

| Переменная | По умолчанию | Описание |
|------------|--------------|-----------|
| `PERSONAL_LMS_DATABASE_URL` | `sqlite:///./instance/personal_lms.db` | URL SQLite (или совместимого драйвера). |
| `PERSONAL_LMS_APP_NAME` | `personal-lms` | Заголовок OpenAPI/metadata. |
| `PERSONAL_LMS_APP_MODE` | `friend_only` | `friend_only` \| `public`. |
| `PERSONAL_LMS_APP_BASE_URL` | пусто | Опционально: базовый URL для доков и будущих абсолютных ссылок. |

Алиасы: `APP_MODE`, `APP_BASE_URL`.

## Cookie-сессия (Starlette `SessionMiddleware`)

| Переменная | По умолчанию | Описание |
|------------|--------------|-----------|
| `PERSONAL_LMS_SESSION_SECRET_KEY` | `change-me-in-env` | Секрет подписи cookie. |
| `PERSONAL_LMS_SESSION_COOKIE_SECURE` | `false` | `https_only`: выставить `true` при работе только по HTTPS. |
| `PERSONAL_LMS_SESSION_COOKIE_SAMESITE` | `lax` | `lax`, `strict` или `none`. |
| `PERSONAL_LMS_SESSION_COOKIE_NAME` | `session` | Имя cookie. |
| `PERSONAL_LMS_SESSION_MAX_AGE` | пусто | TTL сессии в секундах; пустое значение — без ограничения по времени. |

Алиасы: `SESSION_SECRET_KEY`, `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_SAMESITE`, `SESSION_COOKIE_NAME`, `SESSION_MAX_AGE`.

**Примечание.** В Starlette атрибут **HttpOnly** для cookie-сессии включён по умолчанию (см. [SECURITY_NOTES.md](SECURITY_NOTES.md)).

## Feature flags

| Переменная | По умолчанию | Описание |
|------------|--------------|-----------|
| `PERSONAL_LMS_ENABLE_TERMINAL` | `false` | API и UI терминала; исполнение на доверенном хосте, см. [../product/TERMINAL_READINESS.md](../product/TERMINAL_READINESS.md). |
| `PERSONAL_LMS_ENABLE_AI_HELPER` | `true` | Поверхность Lain AI (API/UI); online-режим дополнительно требует ключа OpenAI. |
| `PERSONAL_LMS_ENABLE_PUBLIC_MODE` | `false` | Логируемое напоминание о расхождении с friend-only моделью при совместном использовании с `public`. |
| `PERSONAL_LMS_ENABLE_EXPERIMENTAL_IMPORTS` | `false` | Зарезервировано; на этом этапе только предупреждение в логе при старте. |

Алиасы: `ENABLE_TERMINAL`, `ENABLE_AI_HELPER`, а также **`AI_HELPER_ENABLED`** / **`PERSONAL_LMS_AI_HELPER_ENABLED`** как синонимы для выключателя AI helper.

## OpenAI (опционально)

| Переменная | По умолчанию |
|------------|---------------|
| `PERSONAL_LMS_OPENAI_API_KEY` | пусто |
| `PERSONAL_LMS_AI_HELPER_MODEL` | `gpt-4o-mini` |
| `PERSONAL_LMS_AI_HELPER_TIMEOUT_SECONDS` | `12` |

Пример см. [.env.example](../../.env.example).
