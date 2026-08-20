"""Local in-process orchestration."""

from __future__ import annotations

from typing import Any, Callable

from .base import JobOrchestrator


class LocalOrchestrator(JobOrchestrator):
    def submit(self, job: Any, worker: Callable[[Any], None]) -> None:
        worker(job)

    def get_name(self) -> str:
        return "local"

