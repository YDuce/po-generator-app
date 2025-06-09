#!/usr/bin/env bash
set -euo pipefail

# Ensure pyenv is installed
if ! command -v pyenv &> /dev/null; then
  echo 'pyenv not found. Please install pyenv first.'
  exit 1
fi

PYTHON_VERSION="3.11.8"

# Install Python 3.11 if not already installed
if ! pyenv versions --bare | grep -q "^${PYTHON_VERSION}$"; then
  pyenv install ${PYTHON_VERSION}
fi

pyenv local ${PYTHON_VERSION}

# Create virtualenv if not exists
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt 