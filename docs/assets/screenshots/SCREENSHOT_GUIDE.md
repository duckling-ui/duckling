# Screenshot Guide for Duckling Documentation

This guide lists all screenshots needed for the Duckling documentation. All screenshots should be captured in **dark mode** for consistency with the application's default theme.

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

### 1. Main UI (`ui/` folder)

| Filename | Description | State/Notes |
|----------|-------------|-------------|
| `dropzone-empty.png` | Empty dropzone ready for upload | Initial state, no file selected |
| `dropzone-hover.png` | Dropzone with file hovering | Show drag-over highlight effect |
| `dropzone-uploading.png` | File upload in progress | Show progress indicator |
| `dropzone-batch.png` | Batch mode enabled | Multiple files selected |
| `header.png` | Application header | Show logo, batch toggle, settings button |
| `history-panel.png` | Conversion history panel | Show list of previous conversions |
| `history-search.png` | History with search active | Show search results |

### 2. Settings Panel (`settings/` folder)

| Filename | Description | State/Notes |
|----------|-------------|-------------|
| `settings-ocr.png` | OCR settings section | Show backend dropdown, language, options |
| `settings-ocr-install.png` | OCR backend installation | Show "Install" button for uninstalled backend |
| `settings-ocr-tesseract.png` | Tesseract system install notice | Show the manual installation instructions |
| `settings-tables.png` | Table extraction settings | Show mode selection, options |
| `settings-images.png` | Image extraction settings | Show all image options |
| `settings-enrichment.png` | Document enrichment settings | Show all 4 enrichment toggles |
| `settings-enrichment-warning.png` | Enrichment warning message | Show warning when slow features enabled |
| `settings-performance.png` | Performance settings | Show device, threads, timeout |
| `settings-chunking.png` | RAG chunking settings | Show max tokens, merge peers |
| `settings-output.png` | Output settings | Show default format selection |
| `settings-reset.png` | Reset settings confirmation | Show reset button and confirmation |

### 3. Export Options (`export/` folder)

| Filename | Description | State/Notes |
|----------|-------------|-------------|
| `export-formats.png` | Export format selection | Show all available formats |
| `export-format-selected.png` | Format selected with checkmark | Highlight selected format (e.g., HTML) |
| `preview-markdown-rendered.png` | Markdown preview (rendered) | Show formatted markdown content |
| `preview-markdown-raw.png` | Markdown preview (raw) | Show raw markdown source |
| `preview-html-rendered.png` | HTML preview (rendered) | Show rendered HTML with styling |
| `preview-html-raw.png` | HTML preview (raw) | Show raw HTML source code |
| `preview-json.png` | JSON preview | Show pretty-printed JSON |
| `preview-toggle.png` | Rendered/Raw toggle | Close-up of the toggle buttons |

### 4. Features (`features/` folder)

| Filename | Description | State/Notes |
|----------|-------------|-------------|
| `images-gallery.png` | Extracted images gallery | Show thumbnail grid |
| `images-lightbox.png` | Image lightbox modal | Show full-size image with navigation |
| `images-hover.png` | Image hover actions | Show view/download buttons on hover |
| `tables-list.png` | Extracted tables list | Show table cards with preview |
| `tables-download.png` | Table download options | Show CSV/image download buttons |
| `chunks-list.png` | RAG chunks display | Show chunk cards with metadata |
| `conversion-complete.png` | Conversion success message | Show success header with stats |
| `conversion-progress.png` | Conversion in progress | Show processing indicator |
| `confidence-display.png` | OCR confidence score | Show confidence percentage |

---

## Screenshot Workflow

### Step 1: Start the Application

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Step 2: Prepare Test Documents

Have these ready for capturing different states:
- A PDF with images and tables (for full feature demo)
- A scanned document (for OCR demo)
- A markdown file (for format conversion)
- Multiple small files (for batch mode)

### Step 3: Capture Sequence

1. **Start fresh** - Clear history, reset settings
2. **Capture empty states first** - Dropzone, empty history
3. **Upload a document** - Capture upload states
4. **Capture conversion results** - All export tabs
5. **Open settings** - Capture each section
6. **Toggle preview modes** - Rendered vs raw for MD/HTML

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

After capturing, update this checklist:

### UI Screenshots
- [ ] `ui/dropzone-empty.png`
- [ ] `ui/dropzone-hover.png`
- [ ] `ui/dropzone-uploading.png`
- [ ] `ui/dropzone-batch.png`
- [ ] `ui/header.png`
- [ ] `ui/history-panel.png`
- [ ] `ui/history-search.png`

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

