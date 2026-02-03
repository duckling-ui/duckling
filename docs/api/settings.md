# Settings API

Endpoints for managing conversion settings.

!!! note "Session-Based Storage"
    Settings are stored per-user session in the database. Each user's settings are isolated and don't affect other users, making Duckling safe for multi-user deployments.

## Get All Settings

```http
GET /api/settings
```

### Response

```json
{
  "ocr": {
    "enabled": true,
    "language": "en",
    "force_full_page_ocr": false,
    "backend": "easyocr",
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
  "enrichment": {
    "code_enrichment": false,
    "formula_enrichment": false,
    "picture_classification": false,
    "picture_description": false
  },
  "output": {
    "default_format": "markdown"
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
  }
}
```

---

## Update Settings

```http
PUT /api/settings
Content-Type: application/json
```

### Request Body

```json
{
  "ocr": {
    "language": "de",
    "backend": "tesseract"
  },
  "tables": {
    "mode": "fast"
  }
}
```

### Response

Returns the updated settings object.

---

## Reset Settings to Defaults

```http
POST /api/settings/reset
```

### Response

Returns the default settings object.

---

## Get Supported Formats

```http
GET /api/settings/formats
```

### Response

```json
{
  "input_formats": [
    {"id": "pdf", "name": "PDF Document", "extensions": [".pdf"], "icon": "document"},
    {"id": "docx", "name": "Microsoft Word", "extensions": [".docx"], "icon": "document"},
    {"id": "image", "name": "Image", "extensions": [".png", ".jpg", ".jpeg", ".tiff"], "icon": "image"}
  ],
  "output_formats": [
    {"id": "markdown", "name": "Markdown", "extension": ".md", "mime_type": "text/markdown"},
    {"id": "html", "name": "HTML", "extension": ".html", "mime_type": "text/html"},
    {"id": "json", "name": "JSON", "extension": ".json", "mime_type": "application/json"}
  ]
}
```

---

## OCR Settings

### Get OCR Settings

```http
GET /api/settings/ocr
```

### Update OCR Settings

```http
PUT /api/settings/ocr
Content-Type: application/json
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `auto_install` | boolean | If `true`, automatically install pip-installable backends |

### Response/Request

```json
{
  "ocr": {
    "enabled": true,
    "language": "en",
    "force_full_page_ocr": false,
    "backend": "easyocr",
    "use_gpu": false,
    "confidence_threshold": 0.5,
    "bitmap_area_threshold": 0.05
  },
  "available_languages": [
    {"code": "en", "name": "English"},
    {"code": "de", "name": "German"},
    {"code": "fr", "name": "French"}
  ],
  "available_backends": [
    {"id": "easyocr", "name": "EasyOCR", "description": "General-purpose OCR with GPU support"},
    {"id": "tesseract", "name": "Tesseract", "description": "Classic OCR engine"},
    {"id": "ocrmac", "name": "macOS Vision", "description": "Native macOS OCR (Mac only)"},
    {"id": "rapidocr", "name": "RapidOCR", "description": "Fast OCR with ONNX runtime"}
  ]
}
```

---

## OCR Backend Management

### Get All Backend Status

```http
GET /api/settings/ocr/backends
```

Returns installation status for all OCR backends.

### Response

```json
{
  "backends": [
    {
      "id": "easyocr",
      "name": "EasyOCR",
      "description": "General-purpose OCR with GPU support",
      "installed": true,
      "available": true,
      "error": null,
      "pip_installable": true,
      "requires_system_install": false,
      "platform": null,
      "note": "First run will download language models (~100MB per language)"
    },
    {
      "id": "tesseract",
      "name": "Tesseract",
      "description": "Classic OCR engine",
      "installed": false,
      "available": false,
      "error": "Package not installed",
      "pip_installable": true,
      "requires_system_install": true,
      "platform": null,
      "note": "Requires Tesseract to be installed on your system"
    }
  ],
  "current_platform": "darwin"
}
```

### Check Specific Backend

```http
GET /api/settings/ocr/backends/{backend_id}/check
```

### Response

```json
{
  "backend": "easyocr",
  "installed": true,
  "available": true,
  "error": null,
  "pip_installable": true,
  "requires_system_install": false,
  "note": "First run will download language models"
}
```

### Install Backend

```http
POST /api/settings/ocr/backends/{backend_id}/install
```

Installs a pip-installable OCR backend.

### Response (Success)

```json
{
  "message": "Successfully installed easyocr",
  "success": true,
  "installed": true,
  "available": true,
  "note": "First run will download language models"
}
```

### Response (Already Installed)

```json
{
  "message": "easyocr is already installed and available",
  "already_installed": true
}
```

### Response (Requires System Install)

```json
{
  "message": "Failed to install tesseract",
  "success": false,
  "error": "tesseract requires system-level installation",
  "requires_system_install": true
}
```

---

## Table Settings

### Get Table Settings

```http
GET /api/settings/tables
```

### Update Table Settings

```http
PUT /api/settings/tables
Content-Type: application/json
```

### Request/Response

```json
{
  "tables": {
    "enabled": true,
    "structure_extraction": true,
    "mode": "accurate",
    "do_cell_matching": true
  }
}
```

---

## Image Settings

### Get Image Settings

```http
GET /api/settings/images
```

### Update Image Settings

```http
PUT /api/settings/images
Content-Type: application/json
```

### Request/Response

```json
{
  "images": {
    "extract": true,
    "classify": true,
    "generate_page_images": false,
    "generate_picture_images": true,
    "generate_table_images": true,
    "images_scale": 1.0
  }
}
```

---

## Enrichment Settings

### Get Enrichment Settings

```http
GET /api/settings/enrichment
```

### Response

```json
{
  "enrichment": {
    "code_enrichment": false,
    "formula_enrichment": false,
    "picture_classification": false,
    "picture_description": false
  },
  "options": {
    "code_enrichment": {
      "description": "Enhance code blocks with language detection and syntax highlighting",
      "default": false,
      "note": "May increase processing time"
    },
    "formula_enrichment": {
      "description": "Extract LaTeX representations from mathematical formulas",
      "default": false,
      "note": "Enables better formula rendering in exports"
    },
    "picture_classification": {
      "description": "Classify images by type (figure, chart, diagram, photo, etc.)",
      "default": false,
      "note": "Adds semantic tags to extracted images"
    },
    "picture_description": {
      "description": "Generate descriptive captions for images using AI vision models",
      "default": false,
      "note": "Requires additional model download, significantly increases processing time"
    }
  }
}
```

### Update Enrichment Settings

```http
PUT /api/settings/enrichment
Content-Type: application/json
```

### Request

```json
{
  "code_enrichment": true,
  "formula_enrichment": true
}
```

### Response

```json
{
  "message": "Enrichment settings updated",
  "enrichment": {
    "code_enrichment": true,
    "formula_enrichment": true,
    "picture_classification": false,
    "picture_description": false
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `code_enrichment` | boolean | Enhance code blocks with language detection |
| `formula_enrichment` | boolean | Extract LaTeX from mathematical formulas |
| `picture_classification` | boolean | Classify images by semantic type |
| `picture_description` | boolean | Generate AI captions for images |

!!! warning "Processing Time"
    Enabling `formula_enrichment` and especially `picture_description` can significantly increase document processing time.

---

## Performance Settings

### Get Performance Settings

```http
GET /api/settings/performance
```

### Update Performance Settings

```http
PUT /api/settings/performance
Content-Type: application/json
```

### Request/Response

```json
{
  "performance": {
    "device": "auto",
    "num_threads": 4,
    "document_timeout": null
  }
}
```

---

## Chunking Settings

### Get Chunking Settings

```http
GET /api/settings/chunking
```

### Update Chunking Settings

```http
PUT /api/settings/chunking
Content-Type: application/json
```

### Request/Response

```json
{
  "chunking": {
    "enabled": false,
    "max_tokens": 512,
    "merge_peers": true
  }
}
```

---

## Output Settings

### Get Output Settings

```http
GET /api/settings/output
```

### Update Output Settings

```http
PUT /api/settings/output
Content-Type: application/json
```

### Request/Response

```json
{
  "output": {
    "default_format": "markdown"
  }
}
```

