"""Validation helpers for conversion settings."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from config import DEFAULT_CONVERSION_SETTINGS


def merge_settings(overrides: Dict[str, Any] | None) -> Dict[str, Any]:
    """Merge partial settings into defaults."""
    merged = deepcopy(DEFAULT_CONVERSION_SETTINGS)
    if not overrides:
        return merged
    _merge_dict(merged, overrides)
    return merged


def _merge_dict(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _merge_dict(target[key], value)
        else:
            target[key] = value

