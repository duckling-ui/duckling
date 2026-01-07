# Features

Duckling provides a comprehensive set of features for document conversion.

## Document Upload

### Drag-and-Drop

Simply drag files onto the drop zone for instant upload. The interface validates file types and shows upload progress.

### Batch Processing

Toggle batch mode to upload and convert multiple files at once:

1. Click **Batch Mode** toggle in the header
2. Drag multiple files onto the drop zone
3. Monitor individual progress for each file
4. Download results separately or together

!!! info "Concurrent Processing"
    The job queue processes up to 2 documents simultaneously to prevent memory exhaustion.

## OCR (Optical Character Recognition)

Extract text from scanned documents and images.

### Supported Backends

| Backend | Description | GPU Support | Best For |
|---------|-------------|-------------|----------|
| **EasyOCR** | Multi-language, accurate | Yes (CUDA) | Complex documents |
| **Tesseract** | Classic, reliable | No | Simple documents |
| **macOS Vision** | Native Apple OCR | Apple Neural Engine | Mac users |
| **RapidOCR** | Fast, lightweight | No | Speed-critical |

### Automatic Backend Installation

Duckling can automatically install OCR backends when you select them:

1. Open **Settings** panel
2. Select an OCR backend from the dropdown
3. If the backend is not installed, you'll see an **Install** button
4. Click to automatically install via pip

!!! note "Installation Requirements"
    - **EasyOCR, OcrMac, RapidOCR**: Can be installed automatically via pip
    - **Tesseract**: Requires system-level installation first:
      - macOS: `brew install tesseract`
      - Ubuntu/Debian: `apt-get install tesseract-ocr`
      - Windows: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

The Settings panel shows the status of each backend:

- ✓ **Installed and ready** - Backend is available for use
- ⚠ **Not installed** - Click to install (pip-installable backends)
- ℹ **Requires system installation** - Follow manual installation instructions

### Language Support

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

## Table Extraction

Automatically detect and extract tables from documents.

### Detection Modes

=== "Accurate Mode"

    - Higher precision detection
    - Better cell boundary recognition
    - Slower processing
    - Recommended for complex tables

=== "Fast Mode"

    - Faster processing
    - Good for simple tables
    - May miss complex structures

### Export Options

- **CSV**: Download individual tables as CSV files
- **Image**: Download table as PNG image
- **JSON**: Full table structure in API response

## Image Extraction

Extract embedded images from documents.

### Options

| Option | Description |
|--------|-------------|
| Extract Images | Enable image extraction |
| Classify Images | Tag images (figure, picture, etc.) |
| Generate Page Images | Create images of each page |
| Generate Picture Images | Extract pictures as files |
| Generate Table Images | Extract tables as images |
| Image Scale | Output scale factor (0.1x - 4.0x) |

### Image Preview Gallery

After conversion, extracted images are displayed in a visual gallery:

- **Thumbnail Grid**: View all images as thumbnails in a responsive grid
- **Hover Actions**: Quick access to view and download buttons on hover
- **Lightbox Viewer**: Click any image to view full-size in a modal
- **Navigation**: Use arrow buttons to browse through multiple images
- **Download**: Download individual images directly from the gallery or lightbox

!!! tip "Image Formats"
    All extracted images are saved as PNG format for maximum compatibility.

## RAG Chunking

Generate document chunks optimized for Retrieval-Augmented Generation.

### How It Works

1. Document is split into semantic chunks
2. Each chunk respects document structure
3. Chunks include metadata (headings, page numbers)
4. Undersized chunks can be merged

### Configuration

| Setting | Description | Default |
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
| **JSON** | `.json` | Full document structure (lossless) |
| **Plain Text** | `.txt` | Simple text without formatting |
| **DocTags** | `.doctags` | Tagged document format |
| **Document Tokens** | `.tokens.json` | Token-level representation |
| **RAG Chunks** | `.chunks.json` | Chunks for RAG applications |

### Preview

The export panel shows a preview of the converted content before download.

## Conversion History

Access previously converted documents:

- View conversion status and metadata
- Re-download converted files
- Search history by filename
- View conversion statistics

### History Features

- **Search**: Find documents by filename
- **Filter**: Filter by status (completed, failed)
- **Statistics**: View success rates and format breakdown
- **Export**: Download history as JSON

