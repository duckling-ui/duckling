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

"""PDF font/text preflight and renderer-quality heuristics (issue #68)."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# Cyrillic block used by the issue #68 reproducer diagnostics
_CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
_LATIN_LETTER_RE = re.compile(r"[A-Za-z]")


@dataclass
class FontRiskInfo:
    name: str
    encoding: str
    embedded: bool
    custom_encoding: bool


@dataclass
class PdfPreflightReport:
    """Result of inspecting a PDF before conversion."""

    path: str
    fonts: List[FontRiskInfo] = field(default_factory=list)
    risky_fonts: List[FontRiskInfo] = field(default_factory=list)
    native_text_sample: str = ""
    native_cyrillic_chars: int = 0
    native_latin_letters: int = 0
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def has_font_risk(self) -> bool:
        return bool(self.risky_fonts)


def count_cyrillic(text: str) -> int:
    return len(_CYRILLIC_RE.findall(text or ""))


def count_latin_letters(text: str) -> int:
    return len(_LATIN_LETTER_RE.findall(text or ""))


def _font_tuple_fields(font: Sequence) -> Tuple[str, str, bool]:
    """Normalize PyMuPDF get_fonts() tuples across versions.

    Typical shape: (xref, ext, type, basefont, name, encoding, emb)
    """
    name = ""
    encoding = ""
    embedded = True
    if len(font) >= 7:
        name = str(font[3] or font[4] or "")
        encoding = str(font[5] or "")
        embedded = bool(font[6])
    elif len(font) >= 5:
        name = str(font[3] or font[4] or "")
        encoding = str(font[4] or "") if len(font) > 4 else ""
    return name, encoding, embedded


def inspect_pdf_fonts(path: Path) -> PdfPreflightReport:
    """Inspect fonts and native text; flag non-embedded custom encodings."""
    report = PdfPreflightReport(path=str(path))
    try:
        import fitz  # PyMuPDF
    except ImportError:
        report.error = "PyMuPDF not installed; skipped font preflight"
        report.warnings.append(
            "PDF preflight unavailable (PyMuPDF missing). Full-page OCR/VLM may "
            "silently lose glyphs on PDFs with non-embedded custom-encoded fonts."
        )
        return report

    try:
        doc = fitz.open(path)
    except Exception as exc:  # pragma: no cover - corrupt inputs
        report.error = str(exc)
        report.warnings.append(f"PDF preflight failed to open file: {exc}")
        return report

    try:
        seen: Dict[str, FontRiskInfo] = {}
        text_parts: List[str] = []
        # Cap pages inspected for large docs
        max_pages = min(len(doc), 5)
        for i in range(max_pages):
            page = doc.load_page(i)
            try:
                for font in page.get_fonts(full=True):
                    name, encoding, embedded = _font_tuple_fields(font)
                    key = f"{name}|{encoding}|{embedded}"
                    if key in seen:
                        continue
                    enc_l = encoding.lower()
                    custom = "custom" in enc_l or enc_l in {"identity-h", "identity-v"}
                    info = FontRiskInfo(
                        name=name or "(unnamed)",
                        encoding=encoding or "(unknown)",
                        embedded=embedded,
                        custom_encoding=custom,
                    )
                    seen[key] = info
                    report.fonts.append(info)
                    if (not embedded) and custom:
                        report.risky_fonts.append(info)
            except Exception:
                pass
            try:
                text_parts.append(page.get_text("text") or "")
            except Exception:
                pass

        report.native_text_sample = "\n".join(text_parts)[:8000]
        report.native_cyrillic_chars = count_cyrillic(report.native_text_sample)
        report.native_latin_letters = count_latin_letters(report.native_text_sample)

        if report.risky_fonts:
            names = ", ".join(sorted({f.name for f in report.risky_fonts})[:8])
            report.warnings.append(
                "PDF uses non-embedded font(s) with custom encoding "
                f"({names}). Docling's PDFium page renderer may drop glyphs "
                "(e.g. Cyrillic) before full-page OCR/VLM. Prefer page_renderer="
                "pymupdf, force_backend_text, or OCR mode pdf_aware_layout_regions "
                "(issue #68)."
            )
    finally:
        doc.close()

    return report


def extract_native_text_sample(path: Path, max_pages: int = 5) -> str:
    """Extract native PDF text via PyMuPDF (or empty string if unavailable)."""
    try:
        import fitz
    except ImportError:
        return ""
    try:
        doc = fitz.open(path)
    except Exception:
        return ""
    try:
        parts = []
        for i in range(min(len(doc), max_pages)):
            parts.append(doc.load_page(i).get_text("text") or "")
        return "\n".join(parts)
    finally:
        doc.close()


def detect_script_coverage_mismatch(
    native_text: str,
    export_text: str,
    *,
    min_native_chars: int = 50,
    ratio_threshold: float = 0.2,
) -> Optional[str]:
    """Return a warning if export loses most Cyrillic present in native PDF text.

    This catches the issue #68 failure mode: PDFium raster drops glyphs so OCR/export
    keeps numbers/punctuation while native text still has hundreds of Cyrillic chars.
    """
    native_cyr = count_cyrillic(native_text)
    export_cyr = count_cyrillic(export_text)
    if native_cyr < min_native_chars:
        return None
    if export_cyr / float(native_cyr) >= ratio_threshold:
        return None
    return (
        f"Possible PDF renderer glyph loss: native PDF text has {native_cyr} Cyrillic "
        f"characters but the export only has {export_cyr} "
        f"(ratio {export_cyr / float(native_cyr):.2f} < {ratio_threshold}). "
        "Full-page OCR/VLM may have consumed an incomplete PDFium page image. "
        "Retry with page_renderer=pymupdf or prefer native text "
        "(force_backend_text / pdf_aware_layout_regions). See issue #68."
    )


def script_name_hint(text: str) -> str:
    """Rough script hint for logging (not locale detection)."""
    if count_cyrillic(text) > 20:
        return "cyrillic"
    if any(unicodedata.name(ch, "").startswith("CJK") for ch in (text or "")[:200]):
        return "cjk"
    return "latin-or-other"
