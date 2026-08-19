"""Build an orchestrator from config."""

from __future__ import annotations

from config import SERVER_CONFIG

from .local import LocalOrchestrator
from .rq import RQOrchestrator
from .ray import RayOrchestrator


def get_orchestrator():
    kind = (SERVER_CONFIG.get("engine", {}) or {}).get("kind", "local")
    if kind == "rq":
        return RQOrchestrator()
    if kind == "ray":
        return RayOrchestrator()
    return LocalOrchestrator()

