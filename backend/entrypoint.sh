#!/usr/bin/env sh
# Production entrypoint: one Gunicorn worker for local in-memory jobs; multi-worker for RQ/Ray.
set -eu

ENGINE_KIND="${DUCKLING_ENGINE_KIND:-local}"
TIMEOUT="${DUCKLING_GUNICORN_TIMEOUT:-300}"
BIND="${DUCKLING_GUNICORN_BIND:-0.0.0.0:5001}"

if [ "$ENGINE_KIND" = "local" ]; then
  WORKERS="${DUCKLING_GUNICORN_WORKERS:-1}"
else
  WORKERS="${DUCKLING_GUNICORN_WORKERS:-2}"
fi

# Local engine stores jobs in-process; multiple workers desync status polls (issue #67 B).
if [ "$ENGINE_KIND" = "local" ] && [ "$WORKERS" -gt 1 ]; then
  echo "[entrypoint] WARNING: DUCKLING_ENGINE_KIND=local with WORKERS=$WORKERS; forcing 1 worker for job visibility" >&2
  WORKERS=1
fi

echo "[entrypoint] engine=$ENGINE_KIND workers=$WORKERS bind=$BIND"
exec gunicorn -k uvicorn.workers.UvicornWorker asgi:app \
  --bind "$BIND" \
  --workers "$WORKERS" \
  --timeout "$TIMEOUT" \
  --access-logfile - \
  --error-logfile -
