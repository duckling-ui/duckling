# Settings API

Endpoints for managing conversion settings.

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

