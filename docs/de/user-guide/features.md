# Funktionen

Duckling provides a comprehensive set of features for document conversion.

## Document Upload

### Drag-und-Drop

Simply drag files onto the drop zone for instant upload. The interface validates file types und shows upload progress.

<figure markdown="span">
  ![Dropzone Empty](../assets/screenshots/ui/dropzone-empty.png){ loading=lazy }
  <figcaption>The dropzone ready to receive files</figcaption>
</figure>

### URL Input

Convert documents directly from URLs without downloading them first:

1. Klicken Sie auf die Registerkarte **URLs** über der Ablagezone
2. Fügen Sie eine URL pro Zeile ein (eine Zeile = ein Dokument; mehrere Zeilen starten einen Stapel)
3. Klicken Sie auf **Convert All**
4. Die Dokumente werden heruntergeladen und konvertiert

Supported URL features:

- Automatic file type detection from URL path
- Content-Type header detection for files without extensions
- Content-Disposition header support for filename extraction
- Same file type restrictions as local uploads
- **Automatic image extraction for HTML pages**: When converting HTML from URLs, Duckling automatically downloads all images referenced in the page und makes them available in the Image Preview Gallery

!!! tip "HTML Pages with Images"
    When you convert an HTML page (like a blog post or article), Duckling will:

    1. Herunterladen the HTML content
    2. Find all `<img>` tags und CSS background images
    3. Herunterladen each image from its source URL
    4. Embed the images as base64 data URIs in the HTML
    5. Save the images separately for preview und download

    This ensures that converted HTML documents include all their images, even when viewed offline.

!!! tip "Direct Links"
    Use direct download links, not web page URLs. For example:

    - ✅ `https://example.com/document.pdf`
    - ✅ `https://example.com/blog/article` (HTML pages work too!)
    - ❌ `https://example.com/view/document` (JavaScript-rendered content may not work)

### Mehrere Dateien und Ordner

Laden Sie mehr als eine Datei (oder einen ganzen Ordner) über dieselbe Ablagezone hoch—ohne einen separaten Modus:

1. Dateien ziehen, Ordner wählen oder **Dateien wählen…** für einzelne Dateien nutzen
2. Zur Registerkarte **URLs** wechseln und eine URL pro Zeile einfügen
3. Fortschritt beobachten (ein Job: Standardansicht; mehrere Jobs: Stapelübersicht)
4. Ergebnisse nach abgeschlossener Stapelkonvertierung einzeln oder gesamt herunterladen

<figure markdown="span">
  ![Mehrere Dateien](../assets/screenshots/ui/dropzone-batch.png){ loading=lazy }
  <figcaption>Mehrere Dateien zum Upload ausgewählt</figcaption>
</figure>

#### Mehrere URLs

Das URL-Feld ist immer ein mehrzeiliges Textfeld:

1. Zur Registerkarte **URLs** wechseln
2. Eine URL pro Zeile einfügen
3. Auf **Convert All** klicken

!!! info "Concurrent Verarbeitung"
    The job queue processes up to 2 documents simultaneously to prevent memory exhaustion.

## OCR (Optical Character Recognition)

Extrahieren text from scanned documents und images.

### Supported Backends

| Backend | Beschreibung | GPU-Unterstützung | Am besten für |
|---------|-------------|-------------|----------|
| **EasyOCR** | Multi-language, genau | Yes (CUDA) | Complex documents |
| **Tesseract** | Classic, reliable | No | Simple documents |
| **macOS Vision** | Native Apple OCR | Apple Neural Engine | Mac users |
| **RapidOCR** | Fast, lightweight | No | Speed-critical |

### Automatic Backend Installation

Duckling can automatically install OCR backends when you select them:

1. Open **Einstellungen** panel
2. Select an OCR backend from the dropdown
3. If the backend is not installed, you'll see an **Install** button
4. Click to automatically install via pip

<figure markdown="span">
  ![OCR-Einstellungen](../assets/screenshots/settings/settings-ocr.png){ loading=lazy }
  <figcaption>OCR settings with backend selection</figcaption>
</figure>

!!! note "Installation Requirements"
    - **EasyOCR, OcrMac, RapidOCR**: Can be installed automatically via pip
    - **Tesseract**: Requires system-level installation first:
      - macOS: `brew install tesseract`
      - Ubuntu/Debian: `apt-get install tesseract-ocr`
      - Windows: Herunterladen from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

<figure markdown="span">
  ![Tesseract Install Notice](../assets/screenshots/settings/settings-ocr-tesseract.png){ loading=lazy }
  <figcaption>Tesseract requires manual system installation</figcaption>
</figure>

The Einstellungen panel shows the status of each backend:

- ✓ **Installed und ready** - Backend is available for use
- ⚠ **Not installed** - Click to install (pip-installable backends)
- ℹ **Requires system installation** - Follow manual installation instructions

### Sprache Support

28+ languages including:

- **European**: English, German, French, Spanish, Italian, Portuguese, Dutch, Polish, Russian
- **Asian**: Japanese, Chinese (Simplified/Traditional), Korean, Thai, Vietnamese
- **Middle Eastern**: Arabic, Hebrew, Turkish
- **South Asian**: Hindi

### OCR Options

| Option | Beschreibung |
|--------|-------------|
| Force Full Page OCR | Process entire page vs detected regions |
| GPU Acceleration | Use CUDA for faster processing (EasyOCR) |
| Confidence Threshold | Minimum confidence for results (0-1) |
| Bitmap Area Threshold | Minimum area ratio for bitmap OCR |

## Table Extrahierenion

Automatically detect und extract tables from documents.

### Detection Moduss

=== "Accurate Modus"

    - Hocher precision detection
    - Better cell boundary recognition
    - Slower processing
    - Recommended for complex tables

=== "Fast Modus"

    - Faster processing
    - Good for simple tables
    - May miss complex structures

### Export Options

- **CSV**: Herunterladen individual tables as CSV files
- **Image**: Herunterladen table as PNG image
- **JSON**: Full table structure in API response

## Image Extrahierenion

Eingebettete Bilder extrahieren from documents.

### Options

| Option | Beschreibung |
|--------|-------------|
| Extrahieren Images | Enable image extraction |
| Classify Images | Tag images (figure, picture, etc.) |
| Generate Page Images | Create images of each page |
| Generate Picture Images | Extrahieren pictures as files |
| Generate Table Images | Extrahieren tables as images |
| Image Skalierung | Output scale factor (0.1x - 4.0x) |

### Image Preview Gallery

After conversion, extracted images are displayed in a visual gallery:

- **Thumbnail Grid**: View all images as thumbnails in a responsive grid
- **Hover Actions**: Quick access to view und download buttons on hover
- **Lightbox Viewer**: Click any image to view full-size in a modal
- **Navigation**: Use arrow buttons to browse through multiple images
- **Herunterladen**: Herunterladen individual images directly from the gallery or lightbox

<figure markdown="span">
  ![Image Gallery](../assets/screenshots/features/images-gallery.png){ loading=lazy }
  <figcaption>Extrahierened images displayed as thumbnails</figcaption>
</figure>

<figure markdown="span">
  ![Image Lightbox](../assets/screenshots/features/images-lightbox.png){ loading=lazy }
  <figcaption>Full-size image view with navigation</figcaption>
</figure>

!!! tip "Image Formate"
    All extracted images are saved as PNG format for maximum compatibility.

## Document Enrichment

Enhance your converted documents with advanced AI-powered features.

### Available Enrichments

| Feature | Beschreibung | Impact |
|---------|-------------|--------|
| **Code Enrichment** | Detect programming languages und enhance code blocks | Niedrig |
| **Formula Enrichment** | Extrahieren LaTeX from mathematical equations | Mittel |
| **Picture Classification** | Classify images (figure, chart, diagram, photo) | Niedrig |
| **Picture Beschreibung** | Generate AI captions for images | Hoch |

### Konfiguration

Enable enrichments in the **Einstellungen** panel under **Document Enrichment**:

1. Open Einstellungen (gear icon)
2. Scroll to "Document Enrichment" section
3. Aktivieren desired features on/off
4. Einstellungen are saved automatically

<figure markdown="span">
  ![Enrichment Einstellungen](../assets/screenshots/settings/settings-enrichment.png){ loading=lazy }
  <figcaption>Document Enrichment settings panel</figcaption>
</figure>

!!! warning "Verarbeitung Time"
    Enrichment features, especially **Picture Beschreibung** und **Formula Enrichment**, can significantly increase processing time as they require additional AI model inference. A warning is displayed when these features are enabled.

<figure markdown="span">
  ![Enrichment Warning](../assets/screenshots/settings/settings-enrichment-warning.png){ loading=lazy }
  <figcaption>Warning displayed when slow features are enabled</figcaption>
</figure>

### Code Enrichment

When enabled, code blocks in your documents are enhanced with:

- Automatic programming language detection
- Syntax highlighting metadata
- Improved code structure recognition

### Formula Enrichment

Extrahierens mathematical formulas und converts them to LaTeX:

- Inline equations: `$E = mc^2$`
- Display equations with proper formatting
- Better rendering in HTML und Markdown exports

### Picture Classification

Automatically tags images with semantic types:

- **Figure**: Diagramme, illustrations, schematics
- **Chart**: Bar charts, line graphs, pie charts
- **Photo**: Photographs, screenshots
- **Logo**: Brund logos, icons
- **Table**: Table images (separate from table extraction)

### Picture Beschreibung

Uses vision-language AI models to generate descriptive captions:

- Natural language descriptions of image content
- Useful for accessibility (alt text)
- Enhances searchability of documents
- Requires model download on first use

!!! note "Modusl Requirements"
    Picture Beschreibung requires downloading a vision-language model (~1-2GB). This happens automatically on first use but may take several minutes.

### Pre-Herunterladening Modusls

To avoid delays during document processing, you can pre-download enrichment models:

1. Open **Einstellungen** panel
2. Scroll to **Document Enrichment** section
3. Find the **Pre-Herunterladen Modusls** area at the bottom
4. Click **Herunterladen** next to any model you want to pre-download

| Modusl | Size | Zweck |
|-------|------|---------|
| Picture Classifier | ~350MB | Image type classification |
| Picture Describer | ~2GB | AI image captions |
| Formula Recognizer | ~500MB | LaTeX extraction |
| Code Detector | ~200MB | Programming language detection |

!!! tip "Herunterladen Progress"
    A progress bar shows the download status. Modusls are cached locally after download, so you only need to download them once.

## RAG Chunking

Generate document chunks optimized for Retrieval-Augmented Generation.

### How It Works

1. Document is split into semantic chunks
2. Each chunk respects document structure
3. Chunks include metadata (headings, page numbers)
4. Undersized chunks can be merged

### Konfiguration

| Einstellung | Beschreibung | Stundard |
|---------|-------------|---------|
| Max Tokens | Maximum tokens per chunk | 512 |
| Merge Peers | Merge undersized chunks | true |

### Output Format

```json
{
  "chunks": [
    {
      "id": 1,
      "text": "Introduction to machine learning...",
      "meta": {
        "headings": ["Chapter 1", "Introduction"],
        "page": 1
      }
    }
  ]
}
```

## Export Formate

### Available Formate

| Format | Extension | Beschreibung |
|--------|-----------|-------------|
| **Markdown** | `.md` | Formatted text with headers, lists, links |
| **HTML** | `.html` | Web-ready format with styling |
| **JSON** | `.json` | Vollständige Dokumentstruktur (lossless) |
| **Klartext** | `.txt` | Simple text without formatting |
| **DocTags** | `.doctags` | Tagged document format |
| **Document Tokens** | `.tokens.json` | Token-level representation |
| **RAG Chunks** | `.chunks.json` | Chunks for RAG applications |

<figure markdown="span">
  ![Export Formate](../assets/screenshots/export/export-formats.png){ loading=lazy }
  <figcaption>Available export formats with selection</figcaption>
</figure>

### Preview

The export panel shows a live preview of your converted content that updates as you switch between export formats.

#### Format-Specific Preview

- **Dynamic Content**: Preview automatically loads content for the selected export format
- **Format Badge**: Shows which format you're currently previewing
- **Content Caching**: Previously loaded formats are cached for instant switching

#### Rendered vs Raw Modus

For HTML und Markdown formats, toggle between rendered und raw views:

<figure markdown="span">
  ![Preview Aktivieren](../assets/screenshots/export/preview-toggle.png){ loading=lazy }
  <figcaption>Aktivieren between Rendered und Raw preview modes</figcaption>
</figure>

=== "Rendered Modus"

    - **HTML**: Displays formatted HTML with styling, tables, und links
    - **Markdown**: Renders headers, bold/italic text, code blocks, und links
    - Best for reviewing the final visual appearance

    ![Markdown Rendered](../assets/screenshots/export/preview-markdown-rendered.png){ loading=lazy }

=== "Raw Modus"

    - Shows the actual source code/markup
    - HTML: View raw HTML tags und attributes
    - Markdown: View markdown syntax (# headers, **bold**, etc.)
    - Useful for copying content or debugging formatting issues

    ![Markdown Raw](../assets/screenshots/export/preview-markdown-raw.png){ loading=lazy }

#### Other Formate

- **JSON**: Automatically pretty-printed with proper indentation
- **Klartext**: Displayed as-is
- **DocTags/Tokens**: Raw format display

<figure markdown="span">
  ![JSON Preview](../assets/screenshots/export/preview-json.png){ loading=lazy }
  <figcaption>Pretty-printed JSON output</figcaption>
</figure>

## Konvertierung History

Access previously converted documents:

- View conversion status und metadata
- Re-download converted files
- Search history by filename
- View conversion statistics

### History Funktionen

- **Search**: Find documents by filename
- **Filter**: Filter by status (completed, failed)
- **Export**: Herunterladen history as JSON
- **Reload Documents**: Click on completed history entries to reload the converted document without re-conversion
  - Documents are automatically stored on disk after conversion
  - Vollständige Dokumentstruktur is preserved und can be reloaded instantly
- **Content deduplication**: Same file with identical settings reuses stored output
- **Generate Chunks Now**: When no RAG chunks exist, generate them on demund using current chunking settings (no re-conversion needed)
  - Konvertierungs with matching file content und document-affecting settings (OCR, tables, images) complete instantly from cache
  - Outputs are stored once in a content-addressed store und shared via symlinks
### Statistics Panel

A dedicated slide-in panel for full conversion analytics. Open via the **Statistics** button in der Kopfzeile or the **View full statistics** link in the History panel.

**Übersicht:**

- Total conversions, success/failed counts, success rate
- Average processing time und queue depth

**Storage usage:**

- Uploads, outputs, und total storage

**Breakdowns:**

- Input formats, OCR backends, output formats
- Leistung devices (CPU/CUDA/MPS), source types
- Error categories
- Chunking-enabled count

**Extended metrics:**

- **System**: Hardware type (CPU/CUDA/MPS), CPU count, current CPU usage (Duckling backend process), GPU info
- **Throughput**: Average pages/sec und pages/sec per CPU
- **Konvertierung time distribution**: Median, 95th, und 99th percentile
- **Pages/sec over time**: Chart showing throughput over conversion history
- **Leistung by config**: Pages/sec und conversion time by hardware, OCR backend, und image classifier

### Statistics Panel

A dedicated slide-in panel for full conversion analytics. Open via the **Statistics** button in der Kopfzeile or the **View full statistics** link in the History panel.

**Übersicht:**

- Total conversions, success/failed counts, success rate
- Average processing time und queue depth

**Storage usage:**

- Uploads, outputs, und total storage

**Breakdowns:**

- Input formats, OCR backends, output formats
- Leistung devices (CPU/CUDA/MPS), source types
- Error categories
- Chunking-enabled count

**Extended metrics:**

- **System**: Hardware type (CPU/CUDA/MPS), CPU count, current CPU usage (Duckling backend process), GPU info
- **Throughput**: Average pages/sec und pages/sec per CPU
- **Konvertierung time distribution**: Median, 95th, und 99th percentile
- **Pages/sec over time**: Chart showing throughput over conversion history
- **Leistung by config**: Pages/sec und conversion time by hardware, OCR backend, und image classifier

