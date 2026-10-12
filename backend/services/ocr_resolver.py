"""Resolve OCR settings to an installed backend before conversion starts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

from routes.settings import check_ocr_backend_installed

_FALLBACK_ORDER: List[str] = ["tesseract", "rapidocr", "easyocr", "ocrmac"]


def resolve_ocr_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a copy of settings with OCR backend adjusted to an available engine.

    If no OCR backend is installed, OCR is disabled up front so conversion does not
    waste time on a failing first attempt and concurrent retry storms.
    """
    resolved = deepcopy(settings or {})
    ocr = resolved.get("ocr") or {}
    if not ocr.get("enabled", True):
        return resolved

    backend = ocr.get("backend") or "tesseract"
    if check_ocr_backend_installed(backend).get("available"):
        return resolved

    for candidate in _FALLBACK_ORDER:
        if candidate == backend:
            continue
        if check_ocr_backend_installed(candidate).get("available"):
            ocr = {**ocr, "backend": candidate}
            resolved["ocr"] = ocr
            return resolved

    resolved["ocr"] = {**ocr, "enabled": False}
    return resolved
