"""Tests for fail-closed OCR fallback (issue #67 E)."""

from config import DEFAULT_CONVERSION_SETTINGS
from routes.convert import _history_status_message


def test_history_status_messages_do_not_mislabel_pending():
    assert _history_status_message("pending") == "Conversion queued"
    assert _history_status_message("processing") == "Conversion in progress"
    assert _history_status_message("completed") == "Conversion completed"
    assert _history_status_message("failed") == "Conversion failed"


def test_default_disallows_silent_ocr_fallback():
    assert DEFAULT_CONVERSION_SETTINGS["ocr"].get("allow_fallback_without_ocr") is False
