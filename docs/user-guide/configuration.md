# Configuration Guide

Complete reference for all Duckling configuration options.

## Environment Variables

Create a `.env` file in the `backend` directory:

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

### Production Environment

```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key-here
DEBUG=False
MAX_CONTENT_LENGTH=209715200   # 200MB for production
```

!!! danger "Security Warning"
    Never use the default `SECRET_KEY` in production. Generate a secure random key.

---

## OCR Settings

OCR (Optical Character Recognition) extracts text from images and scanned documents.

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable OCR processing |
| `backend` | string | `"easyocr"` | OCR engine to use |
| `language` | string | `"en"` | Primary language for recognition |
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

    - **GPU Support**: Yes (CUDA)
    - **Languages**: 80+
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

    - **GPU Support**: No
    - **Languages**: 100+
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

    - **GPU Support**: Uses Apple Neural Engine
    - **Requires**: macOS 10.15+

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

    - **GPU Support**: No
    - **Languages**: Limited

### Supported Languages

| Code | Language | Code | Language |
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

## Table Settings

Configure how tables are detected and extracted from documents.

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable table detection |
| `structure_extraction` | boolean | `true` | Preserve table structure |
| `mode` | string | `"accurate"` | Detection mode |
| `do_cell_matching` | boolean | `true` | Match cell content to structure |

### Detection Modes

=== "Accurate Mode"

    ```json
    {
      "tables": {
        "enabled": true,
        "mode": "accurate",
        "do_cell_matching": true
      }
    }
    ```

    - Higher precision table detection
    - Better cell boundary recognition
    - Slower processing
    - Recommended for complex tables

=== "Fast Mode"

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

## Image Settings

Configure image extraction and processing.

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `extract` | boolean | `true` | Extract embedded images |
| `classify` | boolean | `true` | Classify and tag images |
| `generate_page_images` | boolean | `false` | Create images of each page |
| `generate_picture_images` | boolean | `true` | Extract pictures as files |
| `generate_table_images` | boolean | `true` | Extract tables as images |
| `images_scale` | float | `1.0` | Scale factor for images (0.1-4.0) |

### Example Configurations

=== "High Quality"

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

## Performance Settings

Optimize processing speed and resource usage.

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `device` | string | `"auto"` | Processing device |
| `num_threads` | int | `4` | CPU threads (1-32) |
| `document_timeout` | int/null | `null` | Max processing time in seconds |

### Device Options

| Device | Description | Best For |
|--------|-------------|----------|
| `auto` | Automatically select best device | General use |
| `cpu` | Force CPU processing | Servers without GPU |
| `cuda` | NVIDIA GPU acceleration | Linux/Windows with NVIDIA GPU |
| `mps` | Apple Metal Performance Shaders | macOS with Apple Silicon |

### Example Configurations

=== "High Performance (GPU)"

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

## Chunking Settings

Configure document chunking for RAG applications.

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable document chunking |
| `max_tokens` | int | `512` | Maximum tokens per chunk |
| `merge_peers` | boolean | `true` | Merge undersized chunks |

### Example Configurations

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

## Output Settings

Configure default output format.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `default_format` | string | `"markdown"` | Default export format |

---

## Complete Configuration Example

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

## Configuration via API

### Get Current Settings

```bash
curl http://localhost:5001/api/settings
```

### Update Settings

```bash
curl -X PUT http://localhost:5001/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "ocr": {"backend": "tesseract"},
    "performance": {"num_threads": 8}
  }'
```

### Reset to Defaults

```bash
curl -X POST http://localhost:5001/api/settings/reset
```

---

## Troubleshooting

### OCR Not Working

1. **EasyOCR initialization error**: Switch to `ocrmac` (macOS) or `tesseract`
2. **GPU errors**: Set `use_gpu: false`
3. **Low confidence results**: Lower `confidence_threshold`

### Slow Processing

1. Reduce `images_scale` to `0.5`
2. Use `mode: "fast"` for tables
3. Disable `generate_page_images`
4. Increase `num_threads`

### Memory Issues

1. Enable `document_timeout` (e.g., 120 seconds)
2. Process fewer files in batch
3. Reduce `images_scale`
4. Disable chunking if not needed

