"""Routes package."""

from .convert import convert_bp
from .settings import settings_bp
from .history import history_bp

__all__ = ["convert_bp", "settings_bp", "history_bp"]

