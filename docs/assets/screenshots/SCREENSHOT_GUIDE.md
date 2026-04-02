# Screenshot Guide for Duckling Documentation

This guide lists all screenshots needed for the Duckling documentation. All screenshots should be captured in **dark mode** for consistency with the application's default theme.

## Directory Structure

Screenshots are organized by locale. Each locale has its own `images` directory:

- **English (default)**: `docs/images/`
- **Spanish**: `docs/es/images/`
- **French**: `docs/fr/images/`
- **German**: `docs/de/images/`

When capturing screenshots for a specific locale, ensure the UI language is set to that locale before capturing, and save the screenshots in the corresponding locale's `images` directory.

## Capture Settings

- **Resolution**: 1920x1080 or 2x retina (3840x2160)
- **Format**: PNG
- **Theme**: Dark mode (default)
- **Browser**: Chrome or Firefox (for consistent rendering)
- **Window Size**: Maximize or use a consistent width (1400px recommended)

### macOS Screenshot Commands

- `⌘ + Shift + 4` - Select area to capture
- `⌘ + Shift + 4 + Space` - Capture specific window
- `⌘ + Shift + 5` - Screenshot toolbar with options

---

## Required Screenshots

All screenshots listed below should be captured for each locale and stored in the respective locale's `images` directory. For example:
- English: `docs/images/dropzone-empty.png`
- Spanish: `docs/es/images/dropzone-empty.png`
- French: `docs/fr/images/dropzone-empty.png`
- German: `docs/de/images/dropzone-empty.png`

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

