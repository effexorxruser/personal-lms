#!/usr/bin/env bash
# Проверка, что локальный сервер отвечает на /health.
set -euo pipefail

URL="http://127.0.0.1:8000/health"

if out="$(curl -fsS "$URL" 2>&1)"; then
  echo "OK: сервер отвечает на GET /health"
  echo "$out"
  exit 0
fi

echo "FAIL: не удалось получить ответ от $URL"
echo "Убедитесь, что приложение запущено: bash scripts/start_local.sh"
exit 1
