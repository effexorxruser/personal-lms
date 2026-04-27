#!/usr/bin/env bash
# WSL/Linux: idempotent local setup + uvicorn on 0.0.0.0:8000 (LAN-friendly).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -d .venv ]]; then
  echo "Creating .venv ..."
  python3 -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate

echo "Upgrading pip ..."
python -m pip install -U pip

echo "Installing project (editable) ..."
python -m pip install -e .

if [[ ! -f .env ]]; then
  echo "Creating .env from .env.example ..."
  cp .env.example .env
fi

echo "Initializing database ..."
python scripts/init_db.py

LAN_IP=""
if command -v hostname >/dev/null 2>&1; then
  LAN_IP="$(hostname -I 2>/dev/null | awk '{print $1}' | tr -d '[:space:]')" || true
fi

echo ""
echo "=== Personal LMS — локальные URL ==="
echo "  Ноутбук (localhost):  http://127.0.0.1:8000"
if [[ -n "$LAN_IP" ]]; then
  echo "  LAN (best-effort):    http://${LAN_IP}:8000"
  echo "  (На телефоне в той же Wi‑Fi подставьте IP ноутбука, если этот адрес недоступен — см. docs/local/PHONE_ACCESS.md)"
else
  echo "  LAN: не удалось определить IP автоматически."
  echo "  Узнайте адрес интерфейса вручную: ip addr"
  echo "  Подробнее: docs/local/PHONE_ACCESS.md"
fi
echo ""
echo "Проверка health (в другом терминале): bash scripts/health_local.sh"
echo "Запуск uvicorn (Ctrl+C для остановки) ..."
echo ""

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
