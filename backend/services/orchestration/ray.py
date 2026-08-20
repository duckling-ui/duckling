"""Ray orchestration adapter."""

from __future__ import annotations

from typing import Any, Callable

from .base import JobOrchestrator


class RayOrchestrator(JobOrchestrator):
    def __init__(self) -> None:
        self._available = False
        try:
            import ray  # noqa: F401
            self._available = True
        except Exception:
            self._available = False

    def submit(self, job: Any, worker: Callable[[Any], None]) -> None:
        worker(job)

    def get_name(self) -> str:
        return "ray" if self._available else "ray-fallback-local"

