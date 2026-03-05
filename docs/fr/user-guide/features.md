# Fonctionnalités

Duckling provides a comprehensive set of features for document conversion.

## Document Upload

### Drag-et-Drop

Simply drag files onto the drop zone for instant upload. The interface validates file types et shows upload progress.

<figure markdown="span">
  ![Dropzone Empty](../assets/screenshots/ui/dropzone-empty.png){ loading=lazy }
  <figcaption>The dropzone ready to receive files</figcaption>
</figure>

### URL Input

Convert documents directly from URLs without downloading them first:

1. Cliquez sur **URLs** toggle button above the drop zone
2. Enter a document URL (must be HTTP or HTTPS)
3. Click **Convert** or press Enter
4. The document is downloaded et converted automatically

Supported URL features:

- Automatic file type detection from URL path
- Content-Type header detection for files without extensions
- Content-Disposition header support for filename extraction
- Same file type restrictions as local uploads
- **Automatic image extraction for HTML pages**: When converting HTML from URLs, Duckling automatically downloads all images referenced in the page et makes them available in the Image Preview Gallery

!!! tip "HTML Pages with Images"
    When you convert an HTML page (like a blog post or article), Duckling will:

    1. Télécharger the HTML content
    2. Find all `<img>` tags et CSS background images
    3. Télécharger each image from its source URL
    4. Embed the images as base64 data URIs in the HTML
    5. Save the images separately for preview et download

    This ensures that converted HTML documents include all their images, even when viewed offline.

!!! tip "Direct Links"
    Use direct download links, not web page URLs. For example:

    - ✅ `https://example.com/document.pdf`
    - ✅ `https://example.com/blog/article` (HTML pages work too!)
    - ❌ `https://example.com/view/document` (JavaScript-rendered content may not work)

### Traitement par lots

Activer batch mode to upload et convert multiple files at once:

1. Click **Mode lot** toggle dans l'en-tête
2. Glissez plusieurs fichiers dans la zone de dépôt, or switch to URL mode et enter multiple URLs (one per line)
3. Monitor individual progress for each file
4. Télécharger results separately or together

<figure markdown="span">
  ![Mode lot](../assets/screenshots/ui/dropzone-batch.png){ loading=lazy }
  <figcaption>Mode lot avec plusieurs fichiers selected</figcaption>
</figure>

#### Batch URL Mode

In batch mode, the URL input changes to a multi-line textarea:

1. Enable **Mode lot** dans l'en-tête
2. Switch to **URLs** input mode
3. Paste multiple URLs, one per line
4. Click **Convert All**

!!! info "Concurrent Traitement"
    The job queue processes up to 2 documents simultaneously to prevent memory exhaustion.

## OCR (Optical Character Recognition)

Extraire text from scanned documents et images.

### Supported Backends

| Backend | Description | Support GPU | Idéal pour |
|---------|-------------|-------------|----------|
| **EasyOCR** | Multi-language, précis | Yes (CUDA) | Complex documents |
| **Tesseract** | Classic, reliable | No | Simple documents |
| **macOS Vision** | Native Apple OCR | Apple Neural Moteur | Mac users |
| **RapidOCR** | Fast, lightweight | No | Speed-critical |

### Automatic Backend Installation

Duckling can automatically install OCR backends when you select them:

1. Open **Paramètres** panel
2. Select an OCR backend from the dropdown
3. If the backend is not installed, you'll see an **Install** button
4. Click to automatically install via pip

<figure markdown="span">
  ![Paramètres OCR](../assets/screenshots/settings/settings-ocr.png){ loading=lazy }
  <figcaption>OCR settings with backend selection</figcaption>
</figure>

!!! note "Installation Requirements"
    - **EasyOCR, OcrMac, RapidOCR**: Can be installed automatically via pip
    - **Tesseract**: Requires system-level installation first:
      - macOS: `brew install tesseract`
      - Ubuntu/Debian: `apt-get install tesseract-ocr`
      - Windows: Télécharger from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

<figure markdown="span">
  ![Tesseract Install Notice](../assets/screenshots/settings/settings-ocr-tesseract.png){ loading=lazy }
  <figcaption>Tesseract requires manual system installation</figcaption>
</figure>

The Paramètres panel shows the status of each backend:

- ✓ **Installed et ready** - Backend is available for use
- ⚠ **Not installed** - Click to install (pip-installable backends)
- ℹ **Requires system installation** - Follow manual installation instructions

### Langue Support

28+ languages including:

- **European**: English, German, French, Spanish, Italian, Portuguese, Dutch, Polish, Russian
- **Asian**: Japanese, Chinese (Simplified/Traditional), Korean, Thai, Vietnamese
- **Middle Eastern**: Arabic, Hebrew, Turkish
- **South Asian**: Hindi

### OCR Options

| Option | Description |
|--------|-------------|
| Force Full Page OCR | Process entire page vs detected regions |
| GPU Acceleration | Use CUDA for faster processing (EasyOCR) |
| Confidence Threshold | Minimum confidence for results (0-1) |
| Bitmap Area Threshold | Minimum area ratio for bitmap OCR |

## Table Extraireion

Automatically detect et extract tables from documents.

### Detection Modes

=== "Accurate Mode"

    - Élevéer precision detection
    - Better cell boundary recognition
    - Slower processing
    - Recommended for complex tables

=== "Fast Mode"

    - Faster processing
    - Good for simple tables
    - May miss complex structures

### Export Options

- **CSV**: Télécharger individual tables as CSV files
- **Image**: Télécharger table as PNG image
- **JSON**: Full table structure in API response

## Image Extraireion

Extraire les images intégrées from documents.

### Options

| Option | Description |
|--------|-------------|
| Extraire Images | Enable image extraction |
| Classify Images | Tag images (figure, picture, etc.) |
| Generate Page Images | Create images of each page |
| Generate Picture Images | Extraire pictures as files |
| Generate Table Images | Extraire tables as images |
| Image Échelle | Output scale factor (0.1x - 4.0x) |

### Image Preview Gallery

After conversion, extracted images are displayed in a visual gallery:

- **Thumbnail Grid**: View all images as thumbnails in a responsive grid
- **Hover Actions**: Quick access to view et download buttons on hover
- **Lightbox Viewer**: Click any image to view full-size in a modal
- **Navigation**: Use arrow buttons to browse through multiple images
- **Télécharger**: Télécharger individual images directly from the gallery or lightbox

<figure markdown="span">
  ![Image Gallery](../assets/screenshots/features/images-gallery.png){ loading=lazy }
  <figcaption>Extraireed images displayed as thumbnails</figcaption>
</figure>

<figure markdown="span">
  ![Image Lightbox](../assets/screenshots/features/images-lightbox.png){ loading=lazy }
  <figcaption>Full-size image view with navigation</figcaption>
</figure>

!!! tip "Image Formats"
    All extracted images are saved as PNG format for maximum compatibility.

## Document Enrichment

Enhance your converted documents with advanced AI-powered features.

### Available Enrichments

| Feature | Description | Impact |
|---------|-------------|--------|
| **Code Enrichment** | Detect programming languages et enhance code blocks | Faible |
| **Formula Enrichment** | Extraire LaTeX from mathematical equations | Moyen |
| **Picture Classification** | Classify images (figure, chart, diagram, photo) | Faible |
| **Picture Description** | Generate AI captions for images | Élevé |

### Configuration

Enable enrichments in the **Paramètres** panel under **Document Enrichment**:

1. Open Paramètres (gear icon)
2. Scroll to "Document Enrichment" section
3. Activer desired features on/off
4. Paramètres are saved automatically

<figure markdown="span">
  ![Enrichment Paramètres](../assets/screenshots/settings/settings-enrichment.png){ loading=lazy }
  <figcaption>Document Enrichment settings panel</figcaption>
</figure>

!!! warning "Traitement Time"
    Enrichment features, especially **Picture Description** et **Formula Enrichment**, can significantly increase processing time as they require additional AI model inference. A warning is displayed when these features are enabled.

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

Extraires mathematical formulas et converts them to LaTeX:

- Inline equations: `$E = mc^2$`
- Display equations with proper formatting
- Better rendering in HTML et Markdown exports

### Picture Classification

Automatically tags images with semantic types:

- **Figure**: Diagrammes, illustrations, schematics
- **Chart**: Bar charts, line graphs, pie charts
- **Photo**: Photographs, screenshots
- **Logo**: Bret logos, icons
- **Table**: Table images (separate from table extraction)

### Picture Description

Uses vision-language AI models to generate descriptive captions:

- Natural language descriptions of image content
- Useful for accessibility (alt text)
- Enhances searchability of documents
- Requires model download on first use

!!! note "Model Requirements"
    Picture Description requires downloading a vision-language model (~1-2GB). This happens automatically on first use but may take several minutes.

### Pre-Téléchargering Models

To avoid delays during document processing, you can pre-download enrichment models:

1. Open **Paramètres** panel
2. Scroll to **Document Enrichment** section
3. Find the **Pre-Télécharger Models** area at the bottom
4. Click **Télécharger** next to any model you want to pre-download

| Model | Size | Objectif |
|-------|------|---------|
| Picture Classifier | ~350MB | Image type classification |
| Picture Describer | ~2GB | AI image captions |
| Formula Recognizer | ~500MB | LaTeX extraction |
| Code Detector | ~200MB | Programming language detection |

!!! tip "Télécharger Progress"
    A progress bar shows the download status. Models are cached locally after download, so you only need to download them once.

## RAG Chunking

Generate document chunks optimized for Retrieval-Augmented Generation.

### How It Works

1. Document is split into semantic chunks
2. Each chunk respects document structure
3. Chunks include metadata (headings, page numbers)
4. Undersized chunks can be merged

### Configuration

| Paramètre | Description | Par défaut |
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

## Export Formats

### Available Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| **Markdown** | `.md` | Formatted text with headers, lists, links |
| **HTML** | `.html` | Web-ready format with styling |
| **JSON** | `.json` | Structure complète du document (lossless) |
| **Texte brut** | `.txt` | Simple text without formatting |
| **DocTags** | `.doctags` | Tagged document format |
| **Document Tokens** | `.tokens.json` | Token-level representation |
| **RAG Chunks** | `.chunks.json` | Chunks for RAG applications |

<figure markdown="span">
  ![Export Formats](../assets/screenshots/export/export-formats.png){ loading=lazy }
  <figcaption>Available export formats with selection</figcaption>
</figure>

### Preview

The export panel shows a live preview of your converted content that updates as you switch between export formats.

#### Format-Specific Preview

- **Dynamic Content**: Preview automatically loads content for the selected export format
- **Format Badge**: Shows which format you're currently previewing
- **Content Caching**: Previously loaded formats are cached for instant switching

#### Rendered vs Raw Mode

For HTML et Markdown formats, toggle between rendered et raw views:

<figure markdown="span">
  ![Preview Activer](../assets/screenshots/export/preview-toggle.png){ loading=lazy }
  <figcaption>Activer between Rendered et Raw preview modes</figcaption>
</figure>

=== "Rendered Mode"

    - **HTML**: Displays formatted HTML with styling, tables, et links
    - **Markdown**: Renders headers, bold/italic text, code blocks, et links
    - Best for reviewing the final visual appearance

    ![Markdown Rendered](../assets/screenshots/export/preview-markdown-rendered.png){ loading=lazy }

=== "Raw Mode"

    - Shows the actual source code/markup
    - HTML: View raw HTML tags et attributes
    - Markdown: View markdown syntax (# headers, **bold**, etc.)
    - Useful for copying content or debugging formatting issues

    ![Markdown Raw](../assets/screenshots/export/preview-markdown-raw.png){ loading=lazy }

#### Other Formats

- **JSON**: Automatically pretty-printed with proper indentation
- **Texte brut**: Displayed as-is
- **DocTags/Tokens**: Raw format display

<figure markdown="span">
  ![JSON Preview](../assets/screenshots/export/preview-json.png){ loading=lazy }
  <figcaption>Pretty-printed JSON output</figcaption>
</figure>

## Conversion History

Access previously converted documents:

- View conversion status et metadata
- Re-download converted files
- Search history by filename
- View conversion statistics

### History Fonctionnalités

- **Search**: Find documents by filename
- **Filter**: Filter by status (completed, failed)
- **Export**: Télécharger history as JSON
- **Reload Documents**: Click on completed history entries to reload the converted document without re-conversion
  - Documents are automatically stored on disk after conversion
  - Structure complète du document is preserved et can be reloaded instantly
- **Content deduplication**: Same file with identical settings reuses stored output
- **Generate Chunks Now**: When no RAG chunks exist, generate them on demet using current chunking settings (no re-conversion needed)
  - Conversions with matching file content et document-affecting settings (OCR, tables, images) complete instantly from cache
  - Outputs are stored once in a content-addressed store et shared via symlinks
### Statistics Panel

A dedicated slide-in panel for full conversion analytics. Open via the **Statistics** button dans l'en-tête or the **View full statistics** link in the History panel.

**Vue d'ensemble:**

- Total conversions, success/failed counts, success rate
- Average processing time et queue depth

**Storage usage:**

- Uploads, outputs, et total storage

**Breakdowns:**

- Input formats, OCR backends, output formats
- Performances devices (CPU/CUDA/MPS), source types
- Error categories
- Chunking-enabled count

**Extended metrics:**

- **System**: Hardware type (CPU/CUDA/MPS), CPU count, current CPU usage (Duckling backend process), GPU info
- **Throughput**: Average pages/sec et pages/sec per CPU
- **Conversion time distribution**: Median, 95th, et 99th percentile
- **Pages/sec over time**: Chart showing throughput over conversion history
- **Performances by config**: Pages/sec et conversion time by hardware, OCR backend, et image classifier

### Statistics Panel

A dedicated slide-in panel for full conversion analytics. Open via the **Statistics** button dans l'en-tête or the **View full statistics** link in the History panel.

**Vue d'ensemble:**

- Total conversions, success/failed counts, success rate
- Average processing time et queue depth

**Storage usage:**

- Uploads, outputs, et total storage

**Breakdowns:**

- Input formats, OCR backends, output formats
- Performances devices (CPU/CUDA/MPS), source types
- Error categories
- Chunking-enabled count

**Extended metrics:**

- **System**: Hardware type (CPU/CUDA/MPS), CPU count, current CPU usage (Duckling backend process), GPU info
- **Throughput**: Average pages/sec et pages/sec per CPU
- **Conversion time distribution**: Median, 95th, et 99th percentile
- **Pages/sec over time**: Chart showing throughput over conversion history
- **Performances by config**: Pages/sec et conversion time by hardware, OCR backend, et image classifier

