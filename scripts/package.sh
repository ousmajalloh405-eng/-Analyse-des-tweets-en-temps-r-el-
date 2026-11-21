#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="realtime-twitter-sentiment"
OUT="dist/${PROJECT_NAME}.zip"

mkdir -p dist
rm -f "$OUT"

# Exclure secrets, caches, venv, données générées
zip -r "$OUT" . \
  -x ".env" \
  -x ".venv/*" \
  -x "**/__pycache__/*" \
  -x "**/*.pyc" \
  -x ".pytest_cache/*" \
  -x ".ruff_cache/*" \
  -x "dist/*" \
  -x "checkpoints/*" \
  -x ".git/*"

echo "Archive créée : $OUT"
unzip -l "$OUT" | tail -n +1