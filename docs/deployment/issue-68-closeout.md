# Issue #68 closeout notes

Tracking: [duckling-ui/duckling#68](https://github.com/duckling-ui/duckling/issues/68)

| Remediation | Implementation |
|-------------|----------------|
| Separate parser vs page renderer | `pdf.pdf_backend` (parser) + `pdf.page_renderer` (`auto` / `docling_default` / `pymupdf`) |
| MuPDF prerender for OCR/VLM | `services/pdf_renderer.py` + PyMuPDF dependency; Docker Liberation/DejaVu fonts |
| Font preflight | `services/pdf_preflight.py` warns on non-embedded custom-encoded fonts |
| Script coverage mismatch | Cyrillic native-vs-export check → `result.warnings` |
| Prefer native text | `pipeline.force_backend_text` wired; auto-enabled on font risk + default OCR mode |
| Effective renderer metadata | `effective_renderer`, `effective_pdf_backend` on status/result |
| Deprecate `dlparse_v2` | Alias → `docling_parse` with warning; removed from Settings UI as distinct choice |
| Wire `pdf_backend` correctly | Applied on `PdfFormatOption.backend` (was silently dropped from `PdfPipelineOptions`) |

Suggested issue comment after merge:

```text
Fixed in <PR-URL> (branch fix/issue-68-pdfium-cyrillic):

- pdf.page_renderer=auto|docling_default|pymupdf (MuPDF prerender for full-page OCR/VLM)
- Font preflight + Cyrillic coverage mismatch warnings (no silent “success = good text”)
- effective_renderer / effective_pdf_backend on status/result
- dlparse_v2 deprecated alias; pdf_backend actually applied to Docling
- force_backend_text wired; auto-prefer native text on risky fonts + default OCR mode
```

Manual verification with the issue reproducer (`mge-page-2.pdf`, SHA-256
`ed4810d7a4f04ef2059fa46e5a537ee311c4bca1325203ce259fa589b7c28f30`):

1. `page_renderer=pymupdf`, OCR full page, language `ru` → export should retain Cyrillic
2. `page_renderer=docling_default` + full-page OCR → expect `result.warnings` about glyph/coverage loss
