#!/usr/bin/env bash
set -euo pipefail

mkdir -p secrets
echo '{}' > secrets/ci-sa.json
mkdir -p instance

APP_SECRET_KEY=x APP_SERVICE_ACCOUNT_FILE=secrets/ci-sa.json APP_DATABASE_URL=sqlite:///:memory: PYTHONPATH=. alembic upgrade head
# downgrade step omitted in CI

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
mypy --config-file mypy.ini --exclude 'inventory_manager_app/tests/' inventory_manager_app

pytest --cov=inventory_manager_app --cov-fail-under=85 -q
