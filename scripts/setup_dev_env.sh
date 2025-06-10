#!/usr/bin/env bash
set -euo pipefail

# 1) System‐level deps (Linux example; adjust per OS)
sudo apt-get update
sudo apt-get install -y build-essential libpq-dev

# 2) Python venv & runtime deps
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt

# 3) Database migrations
export FLASK_APP=app:create_app
alembic upgrade head

# 4) (Optional) Seed or download any secrets/artifacts
#   e.g., copy service-account JSON into place
