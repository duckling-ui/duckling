"""Configure docling-serve environment before app creation."""

from __future__ import annotations

import os
from typing import Optional

from server_config import get_server_config


def _project_root() -> str:
    from pathlib import Path

    backend_dir = Path(__file__).resolve().parent
    if backend_dir == Path("/app"):
        return str(backend_dir)
    return str(backend_dir.parent)


def apply_docling_serve_env(api_key: Optional[str] = None) -> None:
    """
    Map Duckling server config to docling-serve settings via environment variables.

    Called before ``docling_serve.app.create_app()`` so a single ``DUCKLING_API_KEY``
    secures both ``/api/*`` and ``/v1/*``.
    """
    cfg = get_server_config(_project_root())
    key = (api_key or cfg.get("api_key") or "").strip()
    if key and not os.getenv("DOCLING_SERVE_API_KEY"):
        os.environ["DOCLING_SERVE_API_KEY"] = key

    engine = cfg.get("engine") or {}
    kind = (engine.get("kind") or "local").lower()
    if kind == "rq" and not os.getenv("DOCLING_SERVE_ENGINE"):
        os.environ["DOCLING_SERVE_ENGINE"] = "rq"
        redis_url = engine.get("rq_redis_url") or "redis://redis:6379/0"
        if not os.getenv("DOCLING_SERVE_RQ_REDIS_URL"):
            os.environ["DOCLING_SERVE_RQ_REDIS_URL"] = redis_url
        queue_name = engine.get("rq_queue_name") or "convert"
        if not os.getenv("DOCLING_SERVE_RQ_QUEUE_NAME"):
            os.environ["DOCLING_SERVE_RQ_QUEUE_NAME"] = queue_name

    ray_address = (cfg.get("ray") or {}).get("address") or ""
    if kind == "ray" and ray_address and not os.getenv("DOCLING_SERVE_RAY_ADDRESS"):
        os.environ["DOCLING_SERVE_ENGINE"] = "ray"
        os.environ["DOCLING_SERVE_RAY_ADDRESS"] = ray_address

    log_format = (cfg.get("logging") or {}).get("format") or "text"
    if log_format and not os.getenv("DOCLING_SERVE_LOG_FORMAT"):
        os.environ["DOCLING_SERVE_LOG_FORMAT"] = log_format

    log_level = (cfg.get("logging") or {}).get("level") or "INFO"
    if log_level and not os.getenv("DOCLING_SERVE_LOG_LEVEL"):
        os.environ["DOCLING_SERVE_LOG_LEVEL"] = log_level
