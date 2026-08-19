"""Orchestration interfaces for conversion jobs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class JobOrchestrator(ABC):
    @abstractmethod
    def submit(self, job: Any, worker: Callable[[Any], None]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError

