"""Tests for OCR settings resolution."""

from config import DEFAULT_CONVERSION_SETTINGS
from services.ocr_resolver import resolve_ocr_settings


def test_disables_ocr_when_no_backend_available(monkeypatch):
    monkeypatch.setattr(
        "services.ocr_resolver.check_ocr_backend_installed",
        lambda _backend: {"available": False},
    )
    resolved = resolve_ocr_settings(DEFAULT_CONVERSION_SETTINGS)
    assert resolved["ocr"]["enabled"] is False


def test_keeps_ocr_when_backend_available(monkeypatch):
    monkeypatch.setattr(
        "services.ocr_resolver.check_ocr_backend_installed",
        lambda backend: {"available": backend == "tesseract"},
    )
    settings = {**DEFAULT_CONVERSION_SETTINGS, "ocr": {**DEFAULT_CONVERSION_SETTINGS["ocr"], "backend": "tesseract"}}
    resolved = resolve_ocr_settings(settings)
    assert resolved["ocr"]["enabled"] is True
    assert resolved["ocr"]["backend"] == "tesseract"
