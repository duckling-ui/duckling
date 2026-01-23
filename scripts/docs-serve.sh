#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/venv"
MKDOCS_BIN="$VENV_DIR/bin/mkdocs"
PYTHON_BIN="$VENV_DIR/bin/python"

if [[ -x "$MKDOCS_BIN" ]]; then
  echo "Using MkDocs from: $MKDOCS_BIN"
else
  echo "MkDocs venv not found at $VENV_DIR"
  echo "Creating venv and installing docs dependencies from requirements-docs.txt..."
  python3 -m venv "$VENV_DIR"
  "$PYTHON_BIN" -m pip install --upgrade pip
  "$PYTHON_BIN" -m pip install -r requirements-docs.txt
fi

exec "$MKDOCS_BIN" serve


