#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "[start] Creando entorno virtual..."
    python3 -m venv .venv
fi

echo "[start] Instalando dependencias..."
.venv/bin/pip install -q -r backend/requirements.txt

echo "[start] Iniciando servidor en http://localhost:8080"
.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
