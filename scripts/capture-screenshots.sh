#!/usr/bin/env bash
# Capture Duckling documentation screenshots for all UI locales (en/de/fr/es).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCREENSHOTS_DIR="${ROOT}/scripts/screenshots"
FRONTEND_DIR="${ROOT}/frontend"

echo "==> Installing screenshot tooling dependencies"
cd "${SCREENSHOTS_DIR}"
npm ci
npx playwright install chromium

echo "==> Generating rich sample PDF fixture (tables + images)"
PYTHON_BIN="${ROOT}/venv/bin/python"
if [[ ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="python3"
fi
"${PYTHON_BIN}" -m pip install -q -r "${SCREENSHOTS_DIR}/fixtures/requirements.txt"
"${PYTHON_BIN}" "${SCREENSHOTS_DIR}/fixtures/generate-sample-pdf.py"

if ! curl -sf "http://127.0.0.1:3000" >/dev/null 2>&1; then
  echo "==> Starting frontend dev server on :3000 (background)"
  (cd "${FRONTEND_DIR}" && npm run dev -- --host 127.0.0.1 --port 3000) &
  DEV_PID=$!
  trap 'kill ${DEV_PID} 2>/dev/null || true' EXIT
  for _ in $(seq 1 60); do
    if curl -sf "http://127.0.0.1:3000" >/dev/null 2>&1; then
      break
    fi
    sleep 2
  done
fi

echo "==> Capturing screenshots (${SCREENSHOTS_LIVE_BACKEND:-live backend when healthy}; set SCREENSHOTS_LIVE_BACKEND=0 for mock-only UI)"
export SCREENSHOTS_LIVE_BACKEND="${SCREENSHOTS_LIVE_BACKEND:-1}"
npm run capture

echo "==> Done. PNGs written under docs/assets/screenshots/"
