# Screenshot Guide for Duckling Documentation

This guide lists all screenshots needed for the Duckling documentation. All screenshots should be captured in **dark mode** for consistency with the application's default theme.

## Automated capture (recommended)

Use the Playwright harness under `scripts/screenshots/` to regenerate localized UI screenshots in CI or locally. It drives the frontend at **1400×900 @2x**, sets each locale via `localStorage` (`duckling.locale`), mocks `/api/*` responses (no Docling backend required), and writes PNGs to `docs/assets/screenshots/`.

```bash
# From repo root (installs Playwright + Chromium on first run)
./scripts/capture-screenshots.sh

# Or run directly:
cd scripts/screenshots && npm ci && npx playwright install chromium && npm run capture
```

**CI:** GitHub Actions workflow [`.github/workflows/screenshots.yml`](../../../.github/workflows/screenshots.yml) (`workflow_dispatch`) captures all locales and uploads PNG artifacts for review.

**Currently automated:** main UI, header, dropzone (empty/hover/uploading), history panel + search, settings sections (OCR, tables, images, pipeline, PDF, performance, chunking, enrichment, output, OCR install notice), and—when a live backend is running—PDF conversion/export shots (progress, conversion complete, export formats, preview toggle, markdown/HTML rendered/raw, JSON preview, images gallery/hover, tables list/download, chunks list).

**Sample PDF fixture:** `./scripts/capture-screenshots.sh` regenerates `scripts/screenshots/fixtures/sample-document.pdf` via `fixtures/generate-sample-pdf.py` (requires `reportlab` + `Pillow` from `fixtures/requirements.txt`). The PDF includes headings, body text, two embedded images (logo + chart), and a structured table so `features/images-gallery-*` and `features/tables-download-*` show realistic extracted content.

**Live backend mode (default):** set `SCREENSHOTS_LIVE_BACKEND=1` (default in `./scripts/capture-screenshots.sh`). Playwright clears backend history, uploads `sample-document.pdf`, disables slow enrichment models for faster capture, and waits for real Docling conversion via the backend on `:5001`. Use `SCREENSHOTS_LIVE_BACKEND=0` for mock-only UI captures without conversion.

**Mock-only mode:** skips conversion/export shots that require the backend; settings and empty UI states still capture with mocked `/api/*` responses.

Locale file naming:

| Locale | Main overview | Other shots (example) |
|--------|---------------|------------------------|
| English | `ui/main-english.png` | `settings/settings-ocr.png` |
| German | `ui/main-german.png` | `settings/settings-ocr-de.png` |
| French | `ui/main-french.png` | `settings/settings-ocr-fr.png` |
| Spanish | `ui/main-spanish.png` | `settings/settings-ocr-es.png` |

Stable selectors use `data-testid` / `data-section` hooks in the React UI—see `tests/test_screenshot_automation.py`.

---

## Directory Structure

Screenshots live under **`docs/assets/screenshots/`**, grouped by category (`ui/`, `settings/`, `export/`, `features/`). Documentation pages should reference them with **absolute site-root paths** such as `/assets/screenshots/ui/main-english.png` so localized pages under `/de/`, `/fr/`, and `/es/` do not resolve images under `/de/assets/` (404 → placeholder fallback).

After editing docs or adding new captures, run:

```bash
./scripts/capture-screenshots.sh
python3 scripts/normalize_doc_screenshot_paths.py
python -m pytest tests/test_doc_screenshots.py tests/test_screenshot_automation.py -v
```

Legacy per-locale `docs/images/` paths may still appear in older notes; prefer `docs/assets/screenshots/` for new captures.

When capturing screenshots for a specific locale, ensure the UI language is set to that locale before capturing. The Playwright harness verifies `document.documentElement.lang` and a locale-specific hero heading before each capture.

Localized homepages (`docs/index.md`, `docs/{de,fr,es}/index.md`) must reference `/assets/screenshots/ui/main-{locale}.png` (not bare `main-german.png`, `fr/main-french.png`, or relative `../assets/...` paths).

## Capture Settings

- **Resolution**: 1400×900 viewport at 2× device scale (Playwright default) or 1920×1080 manual
- **Format**: PNG
- **Theme**: Dark mode (default)
- **Browser**: Chromium via Playwright (recommended for CI) or Chrome/Firefox manually
- **Window Size**: 1400px width (Playwright) or maximize manually

### macOS Screenshot Commands (manual fallback)

- `⌘ + Shift + 4` - Select area to capture
- `⌘ + Shift + 4 + Space` - Capture specific window
- `⌘ + Shift + 5` - Screenshot toolbar with options

---

## Required Screenshots

All screenshots listed below should be captured for each locale under `docs/assets/screenshots/`. For example:
- English: `docs/assets/screenshots/ui/dropzone-empty.png`
- German: `docs/assets/screenshots/ui/dropzone-empty-de.png`
- French: `docs/assets/screenshots/ui/dropzone-empty-fr.png`
- Spanish: `docs/assets/screenshots/ui/dropzone-empty-es.png`

### 1. Main UI (`ui/` subdirectory)

| Filename | Description | State/Notes |
|----------|-------------|-------------|
| `ui/dropzone-empty.png` | Empty dropzone ready for upload | Initial state, no file selected |
| `ui/dropzone-hover.png` | Dropzone with file hovering | Show drag-over highlight effect |
| `ui/dropzone-uploading.png` | File upload in progress | Show progress indicator |
| `ui/dropzone-batch.png` | Multi-file upload | Multiple files selected (same default drop zone) |
| `ui/header.png` | Application header | Show logo, settings button, language selector |
| `ui/history-panel.png` | Conversion history panel | Show list of previous conversions |
| `ui/history-search.png` | History with search active | Show search results |
| `ui/main.png` | Main interface overview | Full application view with default language |

### 2. Settings Panel (`settings/` subdirectory)

| Filename | Description | State/Notes |
|----------|-------------|-------------|
| `settings/settings-ocr.png` | OCR settings section | Show backend dropdown, language, options |
| `settings/settings-ocr-install.png` | OCR backend installation | Show "Install" button for uninstalled backend |
| `settings/settings-ocr-tesseract.png` | Tesseract system install notice | Show the manual installation instructions |
| `settings/settings-tables.png` | Table extraction settings | Show mode selection, options |
| `settings/settings-images.png` | Image extraction settings | Show all image options |
| `settings/settings-enrichment.png` | Document enrichment settings | Show all 4 enrichment toggles |
| `settings/settings-enrichment-warning.png` | Enrichment warning message | Show warning when slow features enabled |
| `settings/settings-performance.png` | Performance settings | Show device, threads, timeout |
| `settings/settings-chunking.png` | RAG chunking settings | Show max tokens, merge peers |
| `settings/settings-output.png` | Output settings | Show default format selection |
| `settings/settings-reset.png` | Reset settings confirmation | Show reset button and confirmation |

### 3. Export Options (`export/` subdirectory)

| Filename | Description | State/Notes |
|----------|-------------|-------------|
| `export/export-formats.png` | Export format selection | Show all available formats |
| `export/export-format-selected.png` | Format selected with checkmark | Highlight selected format (e.g., HTML) |
| `export/preview-markdown-rendered.png` | Markdown preview (rendered) | Show formatted markdown content |
| `export/preview-markdown-raw.png` | Markdown preview (raw) | Show raw markdown source |
| `export/preview-html-rendered.png` | HTML preview (rendered) | Show rendered HTML with styling |
| `export/preview-html-raw.png` | HTML preview (raw) | Show raw HTML source code |
| `export/preview-json.png` | JSON preview | Show pretty-printed JSON |
| `export/preview-toggle.png` | Rendered/Raw toggle | Close-up of the toggle buttons |

### 4. Features (`features/` subdirectory)

| Filename | Description | State/Notes |
|----------|-------------|-------------|
| `features/images-gallery.png` | Extracted images gallery | Show thumbnail grid |
| `features/images-lightbox.png` | Image lightbox modal | Show full-size image with navigation |
| `features/images-hover.png` | Image hover actions | Show view/download buttons on hover |
| `features/tables-list.png` | Extracted tables list | Show table cards with preview |
| `features/tables-download.png` | Table download options | Show CSV/image download buttons |
| `features/chunks-list.png` | RAG chunks display | Show chunk cards with metadata |
| `features/conversion-complete.png` | Conversion success message | Show success header with stats |
| `features/conversion-progress.png` | Conversion in progress | Show processing indicator |
| `features/confidence-display.png` | OCR confidence score | Show confidence percentage |

---

## Screenshot Workflow

### Step 1: Start the Application

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python duckling.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Step 2: Prepare Test Documents

Have these ready for capturing different states:
- A PDF with images and tables (for full feature demo)
- A scanned document (for OCR demo)
- A markdown file (for format conversion)
- Multiple small files (multi-file upload state)

### Step 3: Capture Sequence

1. **Set language** - Switch UI to target locale before capturing
2. **Start fresh** - Clear history, reset settings
3. **Capture empty states first** - Dropzone, empty history
4. **Upload a document** - Capture upload states
5. **Capture conversion results** - All export tabs
6. **Open settings** - Capture each section (ensure UI is in target language)
7. **Toggle preview modes** - Rendered vs raw for MD/HTML
8. **Save to correct directory** - Save screenshots to `<locale>/images/` directory

### Step 4: Post-Processing

1. Crop to remove browser chrome if needed
2. Ensure consistent dimensions
3. Optimize file size (use `pngquant` or similar)
4. Verify dark mode colors are correct

---

## File Naming Convention

- Use lowercase with hyphens: `settings-ocr.png`
- Be descriptive: `preview-markdown-rendered.png`
- Include state when relevant: `dropzone-hover.png`

---

## Placeholder Status

After capturing, update this checklist for each locale. Screenshots should be stored in:
- English: `docs/images/`
- Spanish: `docs/es/images/`
- French: `docs/fr/images/`
- German: `docs/de/images/`

### UI Screenshots
- [ ] `ui/dropzone-empty.png`
- [ ] `ui/dropzone-hover.png`
- [ ] `ui/dropzone-uploading.png`
- [ ] `ui/dropzone-batch.png`
- [ ] `ui/header.png`
- [ ] `ui/history-panel.png`
- [ ] `ui/history-search.png`
- [ ] `ui/main.png`

### Settings Screenshots
- [ ] `settings/settings-ocr.png`
- [ ] `settings/settings-ocr-install.png`
- [ ] `settings/settings-ocr-tesseract.png`
- [ ] `settings/settings-tables.png`
- [ ] `settings/settings-images.png`
- [ ] `settings/settings-enrichment.png`
- [ ] `settings/settings-enrichment-warning.png`
- [ ] `settings/settings-performance.png`
- [ ] `settings/settings-chunking.png`
- [ ] `settings/settings-output.png`
- [ ] `settings/settings-reset.png`

### Export Screenshots
- [ ] `export/export-formats.png`
- [ ] `export/export-format-selected.png`
- [ ] `export/preview-markdown-rendered.png`
- [ ] `export/preview-markdown-raw.png`
- [ ] `export/preview-html-rendered.png`
- [ ] `export/preview-html-raw.png`
- [ ] `export/preview-json.png`
- [ ] `export/preview-toggle.png`

### Feature Screenshots
- [ ] `features/images-gallery.png`
- [ ] `features/images-lightbox.png`
- [ ] `features/images-hover.png`
- [ ] `features/tables-list.png`
- [ ] `features/tables-download.png`
- [ ] `features/chunks-list.png`
- [ ] `features/conversion-complete.png`
- [ ] `features/conversion-progress.png`
- [ ] `features/confidence-display.png`

## Locale-Specific Notes

When capturing screenshots for each locale:
- **English**: Save to `docs/images/`
- **Spanish**: Save to `docs/es/images/` - Ensure UI language is set to Español
- **French**: Save to `docs/fr/images/` - Ensure UI language is set to Français
- **German**: Save to `docs/de/images/` - Ensure UI language is set to Deutsch

All screenshots should maintain the same structure (subdirectories: `ui/`, `settings/`, `export/`, `features/`) within each locale's `images` directory.

