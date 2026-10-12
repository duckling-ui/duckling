"""
ASGI entrypoint: docling-serve (FastAPI) with Duckling Flask mounted at /api.

Production:
  gunicorn -k uvicorn.workers.UvicornWorker asgi:app --bind 0.0.0.0:5001

Development:
  uvicorn asgi:app --host 0.0.0.0 --port 5001 --reload
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

from docling_serve_bootstrap import apply_docling_serve_env  # noqa: E402

apply_docling_serve_env(api_key=os.getenv("DUCKLING_API_KEY"))

try:
    from docling_serve.app import create_app as create_docling_app
    from starlette.middleware.wsgi import WSGIMiddleware

    from duckling import create_app as create_flask_app

    os.environ["DUCKLING_ASGI_MOUNTED"] = "1"
    flask_app = create_flask_app()
    _docling_app = create_docling_app()
    _docling_app.mount("/api", WSGIMiddleware(flask_app))
    app = _docling_app
    DOCLING_SERVE_ENABLED = True
except ImportError as exc:
    logger.warning(
        "docling-serve not installed (%s); falling back to Flask-only WSGI at /api",
        exc,
    )
    os.environ.pop("DUCKLING_ASGI_MOUNTED", None)
    from duckling import create_app as create_flask_app

    app = create_flask_app()
    DOCLING_SERVE_ENABLED = False
