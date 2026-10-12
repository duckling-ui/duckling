"""RQ orchestration adapter (docling-jobkit integration)."""

from __future__ import annotations

from typing import Any, Callable

from .base import JobOrchestrator


class RQOrchestrator(JobOrchestrator):
    def __init__(self) -> None:
        self._available = False
        try:
            import rq  # noqa: F401
            import docling_jobkit  # noqa: F401

            self._available = True
        except Exception:
            self._available = False

    def submit(self, job: Any, worker: Callable[[Any], None]) -> None:
        # docling-serve RQ workers process /v1 tasks; legacy in-process jobs use local worker.
        worker(job)

    def get_name(self) -> str:
        return "rq" if self._available else "rq-fallback-local"
