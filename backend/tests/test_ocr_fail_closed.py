"""Unit tests for OCR fail-closed vs opt-in fallback in ConverterService."""

from unittest.mock import patch

from services.converter import ConversionJob, ConversionStatus, ConverterService


def _make_job(allow_fallback: bool) -> ConversionJob:
    settings = {
        "ocr": {
            "enabled": True,
            "backend": "tesseract",
            "language": "en",
            "allow_fallback_without_ocr": allow_fallback,
        },
        "tables": {"enabled": False, "structure_extraction": False},
        "images": {"extract": False},
        "enrichment": {},
        "performance": {"device": "cpu", "num_threads": 1},
        "pdf": {},
        "pipeline": {},
        "chunking": {"enabled": False},
    }
    return ConversionJob("job-ocr-test", "/tmp/fake.pdf", "fake.pdf", settings=settings)


def test_ocr_error_fails_closed_when_fallback_disabled(tmp_path):
    svc = ConverterService.__new__(ConverterService)
    job = _make_job(allow_fallback=False)
    pdf = tmp_path / "fake.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    job.input_path = str(pdf)

    with patch.object(svc, "_get_converter", side_effect=RuntimeError("No module named 'tesserocr'")):
        with patch("services.converter.resolve_ocr_settings", side_effect=lambda s: s):
            with patch("services.converter.content_store_exists", return_value=False):
                with patch("services.converter.compute_file_hash", return_value="h"):
                    with patch("services.converter.compute_settings_hash", return_value="s"):
                        with patch("services.converter.compute_content_hash", return_value="c"):
                            svc._run_conversion(job)

    assert job.status == ConversionStatus.FAILED
    assert job.error
    assert "tesserocr" in job.error.lower() or "no module" in job.error.lower()


def test_ocr_error_sets_warning_when_fallback_enabled(tmp_path):
    """Opt-in fallback path: first OCR failure then successful no-OCR convert."""
    from unittest.mock import MagicMock

    svc = ConverterService.__new__(ConverterService)
    job = _make_job(allow_fallback=True)
    pdf = tmp_path / "fake.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    job.input_path = str(pdf)

    mock_result = MagicMock()
    mock_result.status.name = "SUCCESS"
    mock_result.pages = []
    mock_result.errors = None
    doc = MagicMock()
    doc.export_to_markdown.return_value = "text"
    doc.export_to_html.return_value = "<p>text</p>"
    doc.export_to_dict.return_value = {}
    doc.export_to_text.return_value = "text"
    doc.export_to_doctags.return_value = "tags"
    doc.pictures = []
    doc.tables = []
    mock_result.document = doc

    converter = MagicMock()
    converter.convert.return_value = mock_result
    n = {"calls": 0}

    def get_converter(_settings):
        n["calls"] += 1
        if n["calls"] == 1:
            raise RuntimeError("tesseract OCR failed: meta tensor")
        return converter

    with patch.object(svc, "_get_converter", side_effect=get_converter):
        with patch.object(svc, "_calculate_confidence", return_value=0.9):
            with patch.object(svc, "_extract_images", return_value=[]):
                with patch.object(svc, "_extract_tables", return_value=[]):
                    with patch.object(svc, "_generate_chunks", return_value=[]):
                        with patch("services.converter.resolve_ocr_settings", side_effect=lambda s: s):
                            with patch("services.converter.content_store_exists", return_value=False):
                                with patch("services.converter.compute_file_hash", return_value="h"):
                                    with patch("services.converter.compute_settings_hash", return_value="s"):
                                        with patch("services.converter.compute_content_hash", return_value="uniquehash"):
                                            with patch("services.converter.OUTPUT_FOLDER", tmp_path):
                                                with patch(
                                                    "services.converter.get_content_store_path",
                                                    return_value=tmp_path / "content-store" / "uniquehash",
                                                ):
                                                    with patch("services.converter.save_metadata"):
                                                        svc._run_conversion(job)

    assert job.status == ConversionStatus.COMPLETED
    assert job.ocr_backend_used == "none"
    assert job.ocr_warning
    assert "OCR was requested" in job.ocr_warning
