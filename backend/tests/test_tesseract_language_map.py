"""Tests for Tesseract language mapping and CLI OCR options (issue #67 C/D)."""

from services.converter import (
    ConverterService,
    TesseractCliOcrOptions,
    _normalize_ocr_language,
)


def test_normalize_tesseract_en_ru():
    assert _normalize_ocr_language("tesseract", "en") == ["eng"]
    assert _normalize_ocr_language("tesseract", "ru") == ["rus"]


def test_normalize_tesseract_multilingual():
    assert _normalize_ocr_language("tesseract", "en+ru") == ["eng", "rus"]
    assert _normalize_ocr_language("tesseract", ["en", "de"]) == ["eng", "deu"]


def test_normalize_tesseract_passthrough_traineddata():
    assert _normalize_ocr_language("tesseract", "eng") == ["eng"]


def test_get_ocr_options_uses_tesseract_cli():
    svc = ConverterService.__new__(ConverterService)
    opts = svc._get_ocr_options({
        "ocr": {"enabled": True, "backend": "tesseract", "language": "en"},
    })
    assert isinstance(opts, TesseractCliOcrOptions)
    assert "eng" in (opts.lang or [])
