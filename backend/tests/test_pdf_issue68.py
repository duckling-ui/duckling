"""Regression tests for issue #68 (PDFium glyph loss / MuPDF prerender)."""

from pathlib import Path

import pytest

from config import DEFAULT_CONVERSION_SETTINGS
from services.pdf_backends import (
    RENDERER_FAMILY_PDFIUM,
    RENDERER_FAMILY_PYMUPDF,
    resolve_pdf_backend,
)
from services.pdf_preflight import (
    FontRiskInfo,
    PdfPreflightReport,
    count_cyrillic,
    detect_script_coverage_mismatch,
)
from services.pdf_renderer import resolve_page_renderer
from services.converter import ConverterService


def test_dlparse_v2_is_deprecated_alias():
    resolved = resolve_pdf_backend("dlparse_v2")
    assert resolved.name == "docling_parse"
    assert resolved.renderer_family == RENDERER_FAMILY_PDFIUM
    assert any("deprecated" in w.lower() for w in resolved.warnings)


def test_pypdfium2_shares_pdfium_renderer_family():
    resolved = resolve_pdf_backend("pypdfium2")
    assert resolved.name == "pypdfium2"
    assert resolved.renderer_family == RENDERER_FAMILY_PDFIUM


def test_default_page_renderer_is_auto():
    assert DEFAULT_CONVERSION_SETTINGS["pdf"].get("page_renderer") == "auto"


def test_auto_renderer_selects_pymupdf_on_font_risk_full_page():
    preflight = PdfPreflightReport(
        path="x.pdf",
        risky_fonts=[
            FontRiskInfo(
                name="TimesNewRoman",
                encoding="Custom",
                embedded=False,
                custom_encoding=True,
            )
        ],
    )
    requested, family, warnings = resolve_page_renderer(
        "auto",
        preflight=preflight,
        ocr_enabled=True,
        ocr_mode="full_page",
        pipeline_kind="standard",
    )
    assert requested == "auto"
    # If PyMuPDF is installed in the test env, expect pymupdf; else pdfium with warning.
    try:
        import fitz  # noqa: F401
        assert family == RENDERER_FAMILY_PYMUPDF
        assert any("MuPDF" in w for w in warnings)
    except ImportError:
        assert family == RENDERER_FAMILY_PDFIUM


def test_docling_default_renderer_stays_pdfium():
    preflight = PdfPreflightReport(
        path="x.pdf",
        risky_fonts=[
            FontRiskInfo("Arial", "Custom", False, True),
        ],
    )
    _, family, _ = resolve_page_renderer(
        "docling_default",
        preflight=preflight,
        ocr_enabled=True,
        ocr_mode="full_page",
        pipeline_kind="standard",
    )
    assert family == RENDERER_FAMILY_PDFIUM


def test_script_mismatch_detects_cyrillic_loss():
    native = "А" * 100 + " Дело № МГЭ"
    export = "1.1.\n08.02.2018\n1256,57"
    warning = detect_script_coverage_mismatch(native, export)
    assert warning is not None
    assert "Cyrillic" in warning
    assert count_cyrillic(native) >= 50


def test_script_mismatch_ok_when_export_keeps_cyrillic():
    native = "ПОЛОЖИТЕЛЬНОЕ ЗАКЛЮЧЕНИЕ " * 10
    export = native
    assert detect_script_coverage_mismatch(native, export) is None


def test_get_converter_wires_pdf_backend_class():
    from docling.datamodel.base_models import InputFormat
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

    svc = ConverterService()
    settings = {
        **DEFAULT_CONVERSION_SETTINGS,
        "pdf": {
            **DEFAULT_CONVERSION_SETTINGS["pdf"],
            "pdf_backend": "pypdfium2",
        },
        "ocr": {**DEFAULT_CONVERSION_SETTINGS["ocr"], "enabled": False},
    }
    # Clear cache between runs
    ConverterService._converters.clear()
    converter = svc._get_converter(settings)
    pdf_opt = converter.format_to_options[InputFormat.PDF]
    assert pdf_opt.backend is PyPdfiumDocumentBackend


def test_get_converter_sets_force_backend_text():
    from docling.datamodel.base_models import InputFormat

    svc = ConverterService()
    ConverterService._converters.clear()
    settings = {
        **DEFAULT_CONVERSION_SETTINGS,
        "pipeline": {
            **DEFAULT_CONVERSION_SETTINGS["pipeline"],
            "force_backend_text": True,
        },
        "ocr": {**DEFAULT_CONVERSION_SETTINGS["ocr"], "enabled": False},
    }
    converter = svc._get_converter(settings)
    pdf_opt = converter.format_to_options[InputFormat.PDF]
    assert pdf_opt.pipeline_options.force_backend_text is True


def test_prerender_writes_image_pdf(tmp_path: Path):
    fitz = pytest.importorskip("fitz")
    from services.pdf_renderer import prerender_pdf_with_mupdf

    src = tmp_path / "hello.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello PDFium gap")
    doc.save(src)
    doc.close()

    dst = tmp_path / "prerender.pdf"
    prerender_pdf_with_mupdf(src, dst, dpi=150)
    assert dst.is_file()
    assert dst.stat().st_size > 0
    out = fitz.open(dst)
    try:
        assert len(out) == 1
    finally:
        out.close()
