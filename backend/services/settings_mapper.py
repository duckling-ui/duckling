"""Map Duckling nested settings to docling-serve ConvertDocumentsOptions."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

try:
    from docling.datamodel.service.options import (
        ConvertDocumentsOptions as ConvertDocumentsOptionsModel,
    )

    _HAS_SERVICE_OPTIONS = True
except ImportError:  # pragma: no cover - optional until docling-serve installed
    ConvertDocumentsOptionsModel = None  # type: ignore
    _HAS_SERVICE_OPTIONS = False


_OCR_MODE_MAP = {
    "default": "default",
    "full_page": "full_page",
    "layout_regions": "layout_regions",
    "pdf_aware_layout_regions": "pdf_aware_layout_regions",
}


def duckling_settings_to_options_dict(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Duckling session/job settings to docling-serve ``options`` dict."""
    settings = settings or {}
    ocr = settings.get("ocr") or {}
    tables = settings.get("tables") or {}
    pdf = settings.get("pdf") or {}
    pipeline = settings.get("pipeline") or {}
    enrichment = settings.get("enrichment") or {}
    performance = settings.get("performance") or {}

    options: Dict[str, Any] = {}

    # OCR
    options["do_ocr"] = bool(ocr.get("enabled", True))
    if ocr.get("force_full_page_ocr"):
        options["force_ocr"] = True
    lang = ocr.get("language")
    if lang:
        options["ocr_lang"] = [lang] if isinstance(lang, str) else list(lang)
    mode = ocr.get("mode", "default")
    if mode in _OCR_MODE_MAP:
        options["ocr_preset"] = _OCR_MODE_MAP[mode]

    # PDF / tables / pipeline
    if pdf.get("pdf_backend"):
        options["pdf_backend"] = pdf["pdf_backend"]
    if pdf.get("image_export_mode"):
        options["image_export_mode"] = pdf["image_export_mode"]
    if tables.get("mode"):
        options["table_mode"] = tables["mode"]
    options["do_table_structure"] = bool(tables.get("structure_extraction", True))
    if pipeline.get("kind"):
        options["pipeline"] = pipeline["kind"]

    # Page range and output formats (per-job)
    page_range = settings.get("page_range")
    if isinstance(page_range, (list, tuple)) and len(page_range) == 2:
        options["page_range"] = list(page_range)
    requested = settings.get("requested_output_formats")
    if isinstance(requested, list) and requested:
        options["to_formats"] = requested
    else:
        default_fmt = (settings.get("output") or {}).get("default_format", "markdown")
        options["to_formats"] = [default_fmt]

    # Enrichment flags
    options["do_code_enrichment"] = bool(enrichment.get("code_enrichment", False))
    options["do_formula_enrichment"] = bool(enrichment.get("formula_enrichment", False))
    options["do_picture_classification"] = bool(enrichment.get("picture_classification", False))
    options["do_picture_description"] = bool(enrichment.get("picture_description", False))
    options["do_chart_extraction"] = bool(enrichment.get("chart_extraction", False))

    # Performance hints (when supported by options model)
    device = performance.get("device")
    if device and device != "auto":
        options["accelerator_device"] = device
    num_threads = performance.get("num_threads")
    if num_threads:
        options["num_threads"] = int(num_threads)
    doc_timeout = performance.get("document_timeout")
    if doc_timeout is not None:
        options["document_timeout"] = doc_timeout

    return options


def duckling_settings_to_convert_options(settings: Dict[str, Any]):
    """Return Pydantic ``ConvertDocumentsOptions`` when docling service models are available."""
    payload = duckling_settings_to_options_dict(settings)
    if not _HAS_SERVICE_OPTIONS:
        return payload
    return ConvertDocumentsOptionsModel.model_validate(payload)


def convert_options_to_duckling_settings(options: Dict[str, Any]) -> Dict[str, Any]:
    """Best-effort inverse map for debugging and docs."""
    options = deepcopy(options or {})
    settings: Dict[str, Any] = {
        "ocr": {
            "enabled": options.get("do_ocr", True),
            "force_full_page_ocr": bool(options.get("force_ocr", False)),
            "language": (options.get("ocr_lang") or ["en"])[0],
            "mode": "full_page" if options.get("force_ocr") else "default",
        },
        "pdf": {
            "pdf_backend": options.get("pdf_backend", "docling_parse"),
            "image_export_mode": options.get("image_export_mode", "placeholder"),
        },
        "tables": {
            "structure_extraction": options.get("do_table_structure", True),
            "mode": options.get("table_mode", "accurate"),
        },
        "pipeline": {"kind": options.get("pipeline", "standard")},
        "enrichment": {
            "code_enrichment": options.get("do_code_enrichment", False),
            "formula_enrichment": options.get("do_formula_enrichment", False),
            "picture_classification": options.get("do_picture_classification", False),
            "picture_description": options.get("do_picture_description", False),
            "chart_extraction": options.get("do_chart_extraction", False),
        },
        "output": {"default_format": (options.get("to_formats") or ["markdown"])[0]},
    }
    if options.get("page_range"):
        settings["page_range"] = options["page_range"]
    if options.get("to_formats"):
        settings["requested_output_formats"] = options["to_formats"]
    return settings
