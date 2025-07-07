#!/usr/bin/env bash
set -euo pipefail

APP_SECRET_KEY=x PYTHONPATH=. alembic upgrade head
APP_SECRET_KEY=x PYTHONPATH=. alembic downgrade -1

ruff check .
flake8
mypy --config-file mypy.ini --follow-imports=skip \
  inventory_manager_app/core/utils/validation.py \
  inventory_manager_app/core/services/sheets.py \
  inventory_manager_app/core/services/drive.py \
  inventory_manager_app/api/routes/health.py \
  inventory_manager_app/core/models/base.py \
  inventory_manager_app/core/config/settings.py

pytest --cov=inventory_manager_app -q
