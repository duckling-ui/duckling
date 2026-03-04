# Konfiguration Guide

Complete reference for all Duckling configuration options.

## Umgebungsvariablen

Erstellen Sie eine `.env` file in the `backend` directory:

```env
# Flask Configuration
FLASK_ENV=development          # development | production | testing
SECRET_KEY=your-secret-key     # Required for production
DEBUG=True                     # Enable debug mode

# File Handling
MAX_CONTENT_LENGTH=104857600   # Max upload size in bytes (100MB default)

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///history.db
```

### Produktion Environment

```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key-here
DEBUG=False
MAX_CONTENT_LENGTH=209715200   # 200MB for production
```

!!! danger "Sicherheit Warning"
    Never use the default `SECRET_KEY` in der Produktion. Generate a secure rundom key.

---

## OCR-Einstellungen

OCR (Optical Character Recognition) extracts text from images und scanned documents.

### Konfiguration Options

| Einstellung | Type | Stundard | Beschreibung |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable OCR processing |
| `backend` | string | `"easyocr"` | Zu verwendende OCR-Engine |
| `language` | string | `"en"` | Hauptsprache for recognition |
| `force_full_page_ocr` | boolean | `false` | OCR entire page vs detected regions |
| `use_gpu` | boolean | `false` | Enable GPU acceleration (EasyOCR only) |
| `confidence_threshold` | float | `0.5` | Minimum confidence for results (0-1) |
| `bitmap_area_threshold` | float | `0.05` | Min area ratio for bitmap OCR (0-1) |

### OCR Backends

=== "EasyOCR"

    Best for multi-language documents with accuracy requirements.

    ```json
    {
      "ocr": {
        "backend": "easyocr",
        "use_gpu": true,
        "language": "en"
      }
    }
    ```

    - **GPU-Unterstützung**: Yes (CUDA)
    - **Spraches**: 80+
    - **Note**: May have initialization issues on some systems

=== "Tesseract"

    Classic, reliable OCR engine for simple documents.

    ```json
    {
      "ocr": {
        "backend": "tesseract",
        "language": "eng"
      }
    }
    ```

    - **GPU-Unterstützung**: No
    - **Spraches**: 100+
    - **Requires**: Tesseract installed on system

=== "macOS Vision"

    Native macOS OCR using Apple's Vision framework.

    ```json
    {
      "ocr": {
        "backend": "ocrmac",
        "language": "en"
      }
    }
    ```

    - **GPU-Unterstützung**: Uses Apple Neural Engine
    - **Requires**: macOS 10.15+
    - **Sprache codes**: Duckling accepts short codes like `en`, `de`, `fr` und will normalize them to Vision locale tags (for example `en-US`) during conversion.

=== "RapidOCR"

    Fast, lightweight OCR using ONNX runtime.

    ```json
    {
      "ocr": {
        "backend": "rapidocr",
        "language": "en"
      }
    }
    ```

    - **GPU-Unterstützung**: No
    - **Spraches**: Limited

### Supported Spraches

| Code | Sprache | Code | Sprache |
|------|----------|------|----------|
| `en` | English | `ja` | Japanese |
| `de` | German | `zh` | Chinese (Simplified) |
| `fr` | French | `zh-tw` | Chinese (Traditional) |
| `es` | Spanish | `ko` | Korean |
| `it` | Italian | `ar` | Arabic |
| `pt` | Portuguese | `hi` | Hindi |
| `nl` | Dutch | `th` | Thai |
| `pl` | Polish | `vi` | Vietnamese |
| `ru` | Russian | `tr` | Turkish |

---

## Tabelleneinstellungen

Configure how tables are detected und extracted from documents.

### Konfiguration Options

| Einstellung | Type | Stundard | Beschreibung |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable table detection |
| `structure_extraction` | boolean | `true` | Preserve table structure |
| `mode` | string | `"genau"` | Detection mode |
| `do_cell_matching` | boolean | `true` | Match cell content to structure |

### Detection Moduss

=== "Accurate Modus"

    ```json
    {
      "tables": {
        "enabled": true,
        "mode": "accurate",
        "do_cell_matching": true
      }
    }
    ```

    - Hocher precision table detection
    - Better cell boundary recognition
    - Slower processing
    - Recommended for complex tables

=== "Fast Modus"

    ```json
    {
      "tables": {
        "enabled": true,
        "mode": "fast",
        "do_cell_matching": false
      }
    }
    ```

    - Faster processing
    - Good for simple tables
    - May miss complex structures

---

## Bildeinstellungen

Configure image extraction und processing.

### Konfiguration Options

| Einstellung | Type | Stundard | Beschreibung |
|---------|------|---------|-------------|
| `extract` | boolean | `true` | Eingebettete Bilder extrahieren |
| `classify` | boolean | `true` | Classify und tag images |
| `generate_page_images` | boolean | `false` | Create images of each page |
| `generate_picture_images` | boolean | `true` | Extrahieren pictures as files |
| `generate_table_images` | boolean | `true` | Extrahieren tables as images |
| `images_scale` | float | `1.0` | Skalierung factor for images (0.1-4.0) |

### Example Konfigurations

=== "Hoch Quality"

    ```json
    {
      "images": {
        "extract": true,
        "classify": true,
        "generate_page_images": true,
        "generate_picture_images": true,
        "generate_table_images": true,
        "images_scale": 2.0
      }
    }
    ```

=== "Minimal (Text Only)"

    ```json
    {
      "images": {
        "extract": false,
        "classify": false,
        "generate_page_images": false,
        "generate_picture_images": false,
        "generate_table_images": false
      }
    }
    ```

---

## Leistung Einstellungen

Optimize processing speed und resource usage.

### Konfiguration Options

| Einstellung | Type | Stundard | Beschreibung |
|---------|------|---------|-------------|
| `device` | string | `"auto"` | Verarbeitung device |
| `num_threads` | int | `4` | CPU threads (1-32) |
| `document_timeout` | int/null | `null` | Max processing time in seconds |

### Device Options

| Device | Beschreibung | Am besten für |
|--------|-------------|----------|
| `auto` | Automatically select best device | General use |
| `cpu` | Force CPU processing | Servers without GPU |
| `cuda` | NVIDIA GPU acceleration | Linux/Windows with NVIDIA GPU |
| `mps` | Apple Metal Leistung Shaders | macOS with Apple Silicon |

### Example Konfigurations

=== "Hoch Leistung (GPU)"

    ```json
    {
      "performance": {
        "device": "cuda",
        "num_threads": 8,
        "document_timeout": null
      }
    }
    ```

=== "Resource-Constrained"

    ```json
    {
      "performance": {
        "device": "cpu",
        "num_threads": 2,
        "document_timeout": 60
      }
    }
    ```

=== "Apple Silicon"

    ```json
    {
      "performance": {
        "device": "mps",
        "num_threads": 4,
        "document_timeout": null
      }
    }
    ```

---

## Chunking Einstellungen

Configure document chunking for RAG applications.

### Konfiguration Options

| Einstellung | Type | Stundard | Beschreibung |
|---------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable document chunking |
| `max_tokens` | int | `512` | Maximum tokens per chunk |
| `merge_peers` | boolean | `true` | Merge undersized chunks |

### Example Konfigurations

=== "RAG-Optimized"

    ```json
    {
      "chunking": {
        "enabled": true,
        "max_tokens": 512,
        "merge_peers": true
      }
    }
    ```

=== "Large Context Windows"

    ```json
    {
      "chunking": {
        "enabled": true,
        "max_tokens": 2048,
        "merge_peers": false
      }
    }
    ```

---

## Output Einstellungen

Configure default output format.

| Einstellung | Type | Stundard | Beschreibung |
|---------|------|---------|-------------|
| `default_format` | string | `"markdown"` | Stundard export format |

---

## Complete Konfiguration Example

```json
{
  "ocr": {
    "enabled": true,
    "backend": "easyocr",
    "language": "en",
    "force_full_page_ocr": false,
    "use_gpu": false,
    "confidence_threshold": 0.5,
    "bitmap_area_threshold": 0.05
  },
  "tables": {
    "enabled": true,
    "structure_extraction": true,
    "mode": "accurate",
    "do_cell_matching": true
  },
  "images": {
    "extract": true,
    "classify": true,
    "generate_page_images": false,
    "generate_picture_images": true,
    "generate_table_images": true,
    "images_scale": 1.0
  },
  "performance": {
    "device": "auto",
    "num_threads": 4,
    "document_timeout": null
  },
  "chunking": {
    "enabled": false,
    "max_tokens": 512,
    "merge_peers": true
  },
  "output": {
    "default_format": "markdown"
  }
}
```

---

## Konfiguration via API

### Get Current Einstellungen

```bash
curl http://localhost:5001/api/settings
```

### Update Einstellungen

```bash
curl -X PUT http://localhost:5001/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "ocr": {"backend": "tesseract"},
    "performance": {"num_threads": 8}
  }'
```

### Reset to Stundards

```bash
curl -X POST http://localhost:5001/api/settings/reset
```

---

## Fehlerbehebung

### OCR Not Working

1. **EasyOCR initialization error**: Switch to `ocrmac` (macOS) or `tesseract`
2. **GPU errors**: Setzen `use_gpu: false`
3. **Niedrig confidence results**: Niedriger `confidence_threshold`

### Slow Verarbeitung

1. Reduce `images_scale` to `0.5`
2. Use `mode: "fast"` for tables
3. Disable `generate_page_images`
4. Increase `num_threads`

### Speicherprobleme

1. Enable `document_timeout` (e.g., 120 seconds)
2. Process fewer files in batch
3. Reduce `images_scale`
4. Disable chunking if not needed

