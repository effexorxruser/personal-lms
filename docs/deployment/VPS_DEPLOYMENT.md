# Деплой на VPS (Ubuntu)

Краткая схема для **Production-like** установки без Docker на выделенной машине под друзей или небольшую группу.

## Окружение

- Ubuntu 22.04+ (или совместимый дистрибутив).
- Python **3.11+** (системный пакет или `pyenv`).
- Виртуальное окружение в каталоге приложения, например `venv/`.

## База и файлы

- SQLite по умолчанию: путь из `PERSONAL_LMS_DATABASE_URL`, обычно файл в `instance/personal_lms.db`.
- Учебный контент в каталоге `content/` рядом с приложением — при деплое копируйте его вместе с кодом.
- Убедитесь, что пользователь процесса имеет права на запись в `instance/`.

### Пример установки без Docker

```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv nginx
git clone <repo-url> personal-lms && cd personal-lms
python3.11 -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
# отредактируйте .env: секрет сессии, флаги, production-настройки
alembic upgrade head
python scripts/create_user.py   # или неинтерактивный режим см. scripts/create_user.py -h
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Статические файлы (`/static`, `/assets`) отдаёт приложение через FastAPI mount, как в dev.

## Обратный прокси и HTTPS

Рекомендуется слушать только loopback (`127.0.0.1:8000`) и вынести TLS наружу.

- **Caddy** или **nginx** как reverse proxy: проксирование на `http://127.0.0.1:8000`, редирект HTTP→HTTPS, заголовки `X-Forwarded-Proto` / `Host` (для корректной работы за прокси при необходимости уточните настройки доверия к прокси в будущем — в MVP приложение не разбирает цепочку прокси явно).
- Сертификаты: Let’s Encrypt (если есть публичное имя) или свои сертификаты для приватного DNS.

После включения HTTPS в `.env` выставьте `PERSONAL_LMS_SESSION_COOKIE_SECURE=true` (или `SESSION_COOKIE_SECURE=true` — см. [ENVIRONMENT_CONFIGURATION.md](ENVIRONMENT_CONFIGURATION.md)).

## systemd

Пример unit-файла `/etc/systemd/system/personal-lms.service`:

```ini
[Unit]
Description=personal-lms FastAPI
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/personal-lms
EnvironmentFile=/opt/personal-lms/.env
ExecStart=/opt/personal-lms/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Активация:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now personal-lms
sudo systemctl status personal-lms
```

См. также [ENVIRONMENT_CONFIGURATION.md](ENVIRONMENT_CONFIGURATION.md), [SECURITY_NOTES.md](SECURITY_NOTES.md), [BACKUP_AND_RECOVERY.md](BACKUP_AND_RECOVERY.md).
