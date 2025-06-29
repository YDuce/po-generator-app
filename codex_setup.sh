#!/usr/bin/env bash
set -euo pipefail   # fail fast

# ─── optional system deps (uncomment if you compile wheels) ───
# apt-get update -qq
# apt-get install -y --no-install-recommends gcc
# apt-get clean && rm -rf /var/lib/apt/lists/*

# ─── Python libs ───
pip install --no-cache-dir -r requirements.txt

# ─── DB migration for tests ───
if command -v alembic >/dev/null 2>&1; then
  alembic upgrade head
fi

echo "✅ Codex setup complete."
