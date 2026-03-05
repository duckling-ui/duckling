# Unterstützte Formate

Complete reference for input und output formats supported by Duckling.

## Input Formate

### Documents

| Format | Extensions | Beschreibung | Notes |
|--------|------------|-------------|-------|
| PDF | `.pdf` | Portable Document Format | Full support including scanned PDFs with OCR |
| Word | `.docx` | Microsoft Word | Modusrn format only (not `.doc`) |
| PowerPoint | `.pptx` | Microsoft PowerPoint | Extrahierens text und images from slides |
| Excel | `.xlsx` | Microsoft Excel | Extrahierens tables und data |
| HTML | `.html`, `.htm` | Web pages | Preserves structure und formatting |
| Markdown | `.md`, `.markdown` | Markdown files | Full CommonMark support |

### Images

| Format | Extensions | Beschreibung | Notes |
|--------|------------|-------------|-------|
| PNG | `.png` | Portable Network Graphics | Best for screenshots und diagrams |
| JPEG | `.jpg`, `.jpeg` | Joint Photographic Experts Group | Best for photos |
| TIFF | `.tiff`, `.tif` | Tagged Image Datei Format | Multi-page support |
| GIF | `.gif` | Graphics Interchange Format | First frame only |
| WebP | `.webp` | Web Picture format | Modusrn web format |
| BMP | `.bmp` | Bitmap | Uncompressed images |

### Technical Documents

| Format | Extensions | Beschreibung | Notes |
|--------|------------|-------------|-------|
| AsciiDoc | `.asciidoc`, `.adoc` | Technical documentation | Full AsciiDoc syntax |
| PubMed XML | `.xml` | Scientific articles | PubMed Central format |
| USPTO XML | `.xml` | Patent documents | US Patent format |

## Output Formate

### Text Formate

#### Markdown (`.md`)

Best for documentation und content that needs formatting.

```markdown
# Document Title

## Section 1

This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

#### HTML (`.html`)

Web-ready format with styling preserved.

```html
<h1>Document Title</h1>
<h2>Section 1</h2>
<p>This is a paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
```

#### Klartext (`.txt`)

Simple text without any formatting.

```
Document Title

Section 1

This is a paragraph with bold and italic text.
```

### Structured Formate

#### JSON (`.json`)

Vollständige Dokumentstruktur in JSON format. Lossless representation.

```json
{
  "title": "Document Title",
  "sections": [
    {
      "heading": "Section 1",
      "level": 2,
      "content": [
        {
          "type": "paragraph",
          "text": "This is a paragraph..."
        }
      ]
    }
  ]
}
```

#### DocTags (`.doctags`)

Tagged document format for semantic analysis.

```
<document>
  <title>Document Title</title>
  <section level="2">
    <heading>Section 1</heading>
    <paragraph>This is a paragraph...</paragraph>
  </section>
</document>
```

#### Document Tokens (`.tokens.json`)

Token-level representation for NLP applications.

```json
{
  "tokens": [
    {"text": "Document", "type": "word", "position": 0},
    {"text": "Title", "type": "word", "position": 1}
  ]
}
```

### RAG Formate

#### RAG Chunks (`.chunks.json`)

Document chunks optimized for retrieval-augmented generation.

```json
{
  "chunks": [
    {
      "id": 1,
      "text": "This is the first chunk of text...",
      "meta": {
        "headings": ["Section 1"],
        "page": 1,
        "token_count": 128
      }
    }
  ]
}
```

## Format Selection Guide

| Use Case | Recommended Format |
|----------|-------------------|
| Dokumentation | Markdown |
| Web publishing | HTML |
| Data processing | JSON |
| Search indexing | Klartext |
| NLP/ML pipelines | Document Tokens |
| RAG applications | RAG Chunks |
| Semantic analysis | DocTags |

## API Format Parameter

When using the API, specify the format in the export endpoint:

```bash
# Download as Markdown
curl http://localhost:5001/api/export/{job_id}/markdown

# Download as JSON
curl http://localhost:5001/api/export/{job_id}/json

# Download as HTML
curl http://localhost:5001/api/export/{job_id}/html
```

## MIME Types

| Format | MIME Type |
|--------|-----------|
| Markdown | `text/markdown` |
| HTML | `text/html` |
| JSON | `application/json` |
| Klartext | `text/plain` |
| DocTags | `application/xml` |

