#!/usr/bin/env bash
set -euo pipefail

APP_SECRET_KEY=x PYTHONPATH=. alembic upgrade head
APP_SECRET_KEY=x PYTHONPATH=. alembic downgrade -1

# verify Redis connectivity
python - <<'PY'
import os, redis, sys
url = os.environ.get('APP_REDIS_URL', 'redis://localhost:6379/0')
try:
    redis.Redis.from_url(url).ping()
except Exception as exc:
    print(f'Redis unreachable: {exc}', file=sys.stderr)
    sys.exit(1)
PY

ruff check .
flake8
mypy --config-file mypy.ini --follow-imports=skip \
  inventory_manager_app/core/utils/validation.py \
  inventory_manager_app/core/services/sheets.py \
  inventory_manager_app/core/services/drive.py \
  inventory_manager_app/api/routes/health.py \
  inventory_manager_app/core/models/base.py \
  inventory_manager_app/core/config/settings.py

pytest --cov=inventory_manager_app --cov-fail-under=85 -q
