# Docling UI API Reference

Complete API documentation for the Docling UI backend.

## Base URL

```
http://localhost:5001/api
```

## Authentication

Currently, the API does not require authentication. For production deployments, consider adding authentication middleware.

---

## Health Check

### Check API Health

```http
GET /health
```

**Response**
```json
{
  "status": "healthy",
  "service": "docling-ui-backend"
}
```

---

## Document Conversion

### Upload and Convert Single Document

```http
POST /convert
Content-Type: multipart/form-data
```

**Parameters**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file` | File | Yes | Document to convert |
| `settings` | JSON string | No | Conversion settings override |

**Example Request**
```bash
curl -X POST http://localhost:5001/api/convert \
  -F "file=@document.pdf" \
  -F 'settings={"ocr":{"enabled":true,"language":"en"}}'
```

**Response** (202 Accepted)
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "input_format": "pdf",
  "status": "processing",
  "message": "Conversion started"
}
```

---

### Upload and Convert Multiple Documents (Batch)

```http
POST /convert/batch
Content-Type: multipart/form-data
```

**Parameters**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `files` | File[] | Yes | Documents to convert |
| `settings` | JSON string | No | Conversion settings override |

**Example Request**
```bash
curl -X POST http://localhost:5001/api/convert/batch \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "files=@image.png"
```

**Response** (202 Accepted)
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440001",
      "filename": "doc1.pdf",
      "input_format": "pdf",
      "status": "processing"
    },
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440002",
      "filename": "doc2.pdf",
      "input_format": "pdf",
      "status": "processing"
    },
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440003",
      "filename": "image.png",
      "input_format": "image",
      "status": "processing"
    }
  ],
  "total": 3,
  "message": "Started 3 conversions"
}
```

---

### Get Conversion Status

```http
GET /convert/{job_id}/status
```

**Response** (Processing)
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "message": "Analyzing document with OCR (easyocr, en)..."
}
```

**Response** (Completed)
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "message": "Conversion completed successfully",
  "confidence": 0.92,
  "formats_available": ["markdown", "html", "json", "text", "doctags"],
  "images_count": 3,
  "tables_count": 2,
  "chunks_count": 0,
  "preview": "# Document Title\n\nFirst paragraph..."
}
```

**Response** (Failed)
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "progress": 0,
  "message": "Conversion failed: Invalid PDF format",
  "error": "Invalid PDF format"
}
```

---

### Get Conversion Result

```http
GET /convert/{job_id}/result
```

**Response**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "confidence": 0.92,
  "formats_available": ["markdown", "html", "json", "text", "doctags", "document_tokens"],
  "result": {
    "markdown_preview": "# Document Title\n\nContent preview...",
    "formats_available": ["markdown", "html", "json", "text", "doctags"],
    "page_count": 5,
    "images_count": 3,
    "tables_count": 2,
    "chunks_count": 0,
    "warnings": []
  },
  "images_count": 3,
  "tables_count": 2,
  "chunks_count": 0,
  "completed_at": "2024-01-15T10:30:00Z"
}
```

---

### Get Extracted Images

```http
GET /convert/{job_id}/images
```

**Response**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "images": [
    {
      "id": 1,
      "filename": "image_1.png",
      "path": "/outputs/job_id/images/image_1.png",
      "caption": "Figure 1: Architecture diagram",
      "label": "figure"
    },
    {
      "id": 2,
      "filename": "image_2.png",
      "path": "/outputs/job_id/images/image_2.png",
      "caption": "",
      "label": "picture"
    }
  ],
  "count": 2
}
```

---

### Download Extracted Image

```http
GET /convert/{job_id}/images/{image_id}
```

**Response**: Binary image file (PNG)

---

### Get Extracted Tables

```http
GET /convert/{job_id}/tables
```

**Response**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "tables": [
    {
      "id": 1,
      "label": "table",
      "caption": "Table 1: Sales Data",
      "rows": [
        ["Product", "Q1", "Q2", "Q3", "Q4"],
        ["Widget A", "100", "150", "200", "175"]
      ],
      "csv_path": "/outputs/job_id/tables/table_1.csv",
      "image_path": "/outputs/job_id/tables/table_1.png"
    }
  ],
  "count": 1
}
```

---

### Download Table as CSV

```http
GET /convert/{job_id}/tables/{table_id}/csv
```

**Response**: CSV file

---

### Download Table as Image

```http
GET /convert/{job_id}/tables/{table_id}/image
```

**Response**: Binary image file (PNG)

---

### Get Document Chunks

```http
GET /convert/{job_id}/chunks
```

**Response**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": [
    {
      "id": 1,
      "text": "This is the first chunk of text from the document...",
      "meta": {
        "headings": ["Introduction"],
        "page": 1
      }
    },
    {
      "id": 2,
      "text": "Second chunk continues the content...",
      "meta": {
        "headings": ["Introduction", "Background"],
        "page": 1
      }
    }
  ],
  "count": 2
}
```

---

### Export Document

```http
GET /export/{job_id}/{format}
```

**Supported Formats**: `markdown`, `html`, `json`, `text`, `doctags`, `document_tokens`, `chunks`

**Response**: File download with appropriate MIME type

---

### Delete Job

```http
DELETE /convert/{job_id}
```

**Response**
```json
{
  "message": "Job 550e8400-e29b-41d4-a716-446655440000 deleted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Settings

### Get All Settings

```http
GET /settings
```

**Response**
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

### Update Settings

```http
PUT /settings
Content-Type: application/json
```

**Request Body**
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

**Response**: Updated settings object

---

### Reset Settings to Defaults

```http
POST /settings/reset
```

**Response**: Default settings object

---

### Get Supported Formats

```http
GET /settings/formats
```

**Response**
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

### OCR Settings

```http
GET /settings/ocr
PUT /settings/ocr
```

**Response/Request**
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

### Table Settings

```http
GET /settings/tables
PUT /settings/tables
```

---

### Image Settings

```http
GET /settings/images
PUT /settings/images
```

---

### Performance Settings

```http
GET /settings/performance
PUT /settings/performance
```

---

### Chunking Settings

```http
GET /settings/chunking
PUT /settings/chunking
```

---

### Output Settings

```http
GET /settings/output
PUT /settings/output
```

---

## History

### Get Conversion History

```http
GET /history
```

**Query Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | int | 50 | Maximum entries to return |
| `offset` | int | 0 | Number of entries to skip |
| `status` | string | - | Filter by status |

**Response**
```json
{
  "entries": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document_abc123.pdf",
      "original_filename": "My Document.pdf",
      "input_format": "pdf",
      "status": "completed",
      "confidence": 0.92,
      "file_size": 1048576,
      "created_at": "2024-01-15T10:00:00Z",
      "completed_at": "2024-01-15T10:00:30Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

### Get Recent History

```http
GET /history/recent
```

**Query Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | int | 10 | Maximum entries to return |

---

### Get History Entry

```http
GET /history/{job_id}
```

**Response**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document_abc123.pdf",
  "original_filename": "My Document.pdf",
  "input_format": "pdf",
  "status": "completed",
  "confidence": 0.92,
  "error_message": null,
  "output_path": "/outputs/550e8400.../document.md",
  "settings": {
    "ocr": {"enabled": true}
  },
  "file_size": 1048576,
  "created_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:00:30Z"
}
```

---

### Delete History Entry

```http
DELETE /history/{job_id}
```

**Response**
```json
{
  "message": "Entry deleted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Get History Statistics

```http
GET /history/stats
```

**Response**
```json
{
  "total": 150,
  "completed": 142,
  "failed": 5,
  "pending": 2,
  "processing": 1,
  "success_rate": 94.7,
  "format_breakdown": {
    "pdf": 100,
    "docx": 30,
    "image": 20
  }
}
```

---

### Search History

```http
GET /history/search
```

**Query Parameters**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `limit` | int | No | Maximum results (default: 20) |

**Response**
```json
{
  "entries": [...],
  "query": "invoice",
  "count": 5
}
```

---

### Export History

```http
GET /history/export
```

**Response**: JSON file download with all history entries

---

### Clear All History

```http
DELETE /history
```

**Response**
```json
{
  "message": "All history entries deleted",
  "count": 150
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 202 | Accepted (async operation started) |
| 400 | Bad Request (invalid input) |
| 404 | Not Found |
| 413 | Payload Too Large |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider adding rate limiting middleware.

---

## CORS

The API allows cross-origin requests from the configured frontend origin (default: `http://localhost:3000`).

