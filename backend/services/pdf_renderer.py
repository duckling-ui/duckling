# The MIT License (MIT)
#
# Copyright (c) 2022-present David G. Simmons
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""MuPDF/PyMuPDF page prerender path for OCR/VLM (issue #68)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

from services.pdf_backends import (
    PAGE_RENDERER_CHOICES,
    RENDERER_FAMILY_PDFIUM,
    RENDERER_FAMILY_PYMUPDF,
)
from services.pdf_preflight import PdfPreflightReport

logger = logging.getLogger(__name__)


def pymupdf_available() -> bool:
    try:
        import fitz  # noqa: F401
        return True
    except ImportError:
        return False


def resolve_page_renderer(
    page_renderer: Optional[str],
    *,
    preflight: Optional[PdfPreflightReport],
    ocr_enabled: bool,
    ocr_mode: str,
    pipeline_kind: str,
) -> Tuple[str, str, list[str]]:
    """Choose effective page renderer.

    Returns (requested_or_normalized, effective_renderer_family, warnings).

    - ``docling_default``: Docling PDF backends (PDFium page images)
    - ``pymupdf``: prerasterize with MuPDF before Docling
    - ``auto``: use pymupdf when font risk + full-page OCR or VLM
    """
    warnings: list[str] = []
    requested = (page_renderer or "auto").strip().lower() or "auto"
    if requested not in PAGE_RENDERER_CHOICES:
        warnings.append(
            f"Unknown page_renderer '{page_renderer}'; using 'auto'."
        )
        requested = "auto"

    uses_page_images = (
        pipeline_kind == "vlm"
        or (
            ocr_enabled
            and ocr_mode in {"full_page", "force_full_page"}
        )
    )
    font_risk = bool(preflight and preflight.has_font_risk)

    if requested == "pymupdf":
        if not pymupdf_available():
            warnings.append(
                "page_renderer=pymupdf requested but PyMuPDF is not installed; "
                "falling back to Docling/PDFium page images."
            )
            return requested, RENDERER_FAMILY_PDFIUM, warnings
        return requested, RENDERER_FAMILY_PYMUPDF, warnings

    if requested == "docling_default":
        return requested, RENDERER_FAMILY_PDFIUM, warnings

    # auto
    if font_risk and uses_page_images:
        if pymupdf_available():
            warnings.append(
                "page_renderer=auto selected MuPDF prerender because non-embedded "
                "custom-encoded fonts were detected and full-page OCR/VLM will "
                "consume page images (issue #68)."
            )
            return requested, RENDERER_FAMILY_PYMUPDF, warnings
        warnings.append(
            "page_renderer=auto would prefer MuPDF prerender (font risk + full-page "
            "OCR/VLM) but PyMuPDF is not installed; using Docling/PDFium."
        )
    return requested, RENDERER_FAMILY_PDFIUM, warnings


def prerender_pdf_with_mupdf(
    source: Path,
    destination: Path,
    *,
    dpi: float = 300.0,
) -> Path:
    """Rasterize each page with MuPDF and write an image-only PDF for Docling.

    OCR/VLM then see MuPDF glyphs instead of PDFium's incomplete raster for
    fragile non-embedded custom-encoded fonts.
    """
    import fitz

    source = Path(source)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    src = fitz.open(source)
    out = fitz.open()
    try:
        zoom = float(dpi) / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        for page in src:
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            img_bytes = pix.tobytes("png")
            # Keep PDF page size in points matching the source page
            rect = page.rect
            new_page = out.new_page(width=rect.width, height=rect.height)
            new_page.insert_image(rect, stream=img_bytes)
        out.save(destination, garbage=3, deflate=True)
    finally:
        out.close()
        src.close()

    logger.info(
        "MuPDF prerender wrote %s from %s at dpi=%s",
        destination,
        source,
        dpi,
    )
    return destination
