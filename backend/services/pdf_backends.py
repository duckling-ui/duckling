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

"""Resolve Docling PDF parser backends and page-image renderer families (issue #68)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Type

from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.backend.docling_parse_v2_backend import DoclingParseV2DocumentBackend
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

try:
    from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
except ImportError:  # pragma: no cover - older Docling
    DoclingParseV4DocumentBackend = None  # type: ignore[misc, assignment]

try:
    from docling.backend.managed_pdfium_backend import ManagedPdfiumDocumentBackend
except ImportError:  # pragma: no cover
    ManagedPdfiumDocumentBackend = None  # type: ignore[misc, assignment]


# All Docling PDF backends in 2.118.x rasterize via PDFium for page images used by OCR/VLM.
RENDERER_FAMILY_PDFIUM = "pdfium"
RENDERER_FAMILY_PYMUPDF = "pymupdf"

PDF_BACKEND_CHOICES = [
    "docling_parse",
    "docling_parse_v4",
    "pypdfium2",
    "managed_pdfium",
]

# Deprecated UI aliases → canonical name
PDF_BACKEND_ALIASES = {
    "dlparse_v2": "docling_parse",
    "dlparse_v1": "docling_parse",
}

PAGE_RENDERER_CHOICES = ["auto", "docling_default", "pymupdf"]


@dataclass(frozen=True)
class ResolvedPdfBackend:
    """Resolved Docling PDF backend class plus metadata."""

    name: str
    backend_cls: Type[Any]
    renderer_family: str
    warnings: List[str]


def _backend_map() -> dict[str, Type[Any]]:
    mapping: dict[str, Type[Any]] = {
        "docling_parse": DoclingParseDocumentBackend,
        "dlparse_v2": DoclingParseV2DocumentBackend,
        "pypdfium2": PyPdfiumDocumentBackend,
    }
    if DoclingParseV4DocumentBackend is not None:
        mapping["docling_parse_v4"] = DoclingParseV4DocumentBackend
    if ManagedPdfiumDocumentBackend is not None:
        mapping["managed_pdfium"] = ManagedPdfiumDocumentBackend
    return mapping


def resolve_pdf_backend(name: Optional[str]) -> ResolvedPdfBackend:
    """Map a settings string to a Docling backend class.

    Note: ``dlparse_v2`` is a deprecated compatibility subclass of
    ``DoclingParseDocumentBackend`` and does not provide a different page renderer.
    """
    warnings: List[str] = []
    raw = (name or "docling_parse").strip() or "docling_parse"
    lower = raw.lower()

    if lower in PDF_BACKEND_ALIASES:
        canonical = PDF_BACKEND_ALIASES[lower]
        warnings.append(
            f"PDF backend '{raw}' is a deprecated alias of '{canonical}' "
            "(same PDFium-based page renderer family; see issue #68)."
        )
        lower = canonical

    mapping = _backend_map()
    if lower not in mapping:
        warnings.append(
            f"Unknown PDF backend '{raw}'; falling back to 'docling_parse'."
        )
        lower = "docling_parse"

    # Prefer the non-deprecated class when the user asked for docling_parse
    # after alias rewrite; keep explicit dlparse_v2 only if somehow still selected.
    backend_cls = mapping[lower]
    return ResolvedPdfBackend(
        name=lower,
        backend_cls=backend_cls,
        renderer_family=RENDERER_FAMILY_PDFIUM,
        warnings=warnings,
    )


def available_pdf_backend_names() -> List[str]:
    """Backend names exposed in settings (excludes deprecated aliases)."""
    mapping = _backend_map()
    names = [n for n in PDF_BACKEND_CHOICES if n in mapping]
    if not names:
        names = ["docling_parse", "pypdfium2"]
    return names
