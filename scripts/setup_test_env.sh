#!/usr/bin/env bash
set -e
pip install -q -r requirements.txt
pip install -q coverage
pip check
black --check .
