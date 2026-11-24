#!/usr/bin/env bash
set -euo pipefail
python -m alembic -c backend/alembic.ini upgrade head
python scripts/seed_if_empty.py
exec python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000