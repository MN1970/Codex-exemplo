#!/usr/bin/env bash
#
# Manta 20 — SP Hub cron entrypoint.
# Uso: rodar via crontab a cada hora (ou frequência desejada).
#
#   0 * * * * /path/to/sp_hub/daily_index.sh >> /var/log/sp_hub.log 2>&1
#
# Requer:
#   - SUPABASE_URL, SUPABASE_SERVICE_KEY exportadas (systemd env ou .env source).
#   - `sp_indexer.py` disponível em SP_INDEXER_PATH (roda antes do delta_sync).
#   - venv Python com supabase-py instalado em SP_HUB_VENV.
#
# Comportamento:
#   1. Ativa venv.
#   2. Roda `sp_indexer.py` (atualiza sp_index; existente desde a v4.2).
#   3. Roda `python -m sp_hub.delta_sync` (Fase 2 — feed proativo).
#   4. Exit code != 0 → cron manda alerta por email.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Load env se houver .env no repo root.
if [ -f "${REPO_ROOT}/.env" ]; then
  # shellcheck disable=SC1091
  set -a && . "${REPO_ROOT}/.env" && set +a
fi

VENV="${SP_HUB_VENV:-${REPO_ROOT}/.venv}"
if [ -d "${VENV}" ]; then
  # shellcheck disable=SC1091
  . "${VENV}/bin/activate"
fi

INDEXER="${SP_INDEXER_PATH:-}"
if [ -n "${INDEXER}" ] && [ -f "${INDEXER}" ]; then
  echo "[daily_index] running sp_indexer at ${INDEXER}"
  python "${INDEXER}"
else
  echo "[daily_index] SP_INDEXER_PATH não definido; pulando indexer (delta_sync ainda roda sobre o sp_index existente)"
fi

echo "[daily_index] running delta_sync"
cd "${REPO_ROOT}"
python -m sp_hub.delta_sync
