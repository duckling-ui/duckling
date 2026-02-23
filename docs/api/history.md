# History API

Endpoints for accessing conversion history.

## Get Conversion History

```http
GET /api/history
```

### Query Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | int | 50 | Maximum entries to return |
| `offset` | int | 0 | Number of entries to skip |
| `status` | string | - | Filter by status |

### Response

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

## Get Recent History

```http
GET /api/history/recent
```

### Query Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | int | 10 | Maximum entries to return |

---

## Get History Entry

```http
GET /api/history/{job_id}
```

### Response

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
  "document_json_path": "/outputs/550e8400.../document.json",
  "settings": {
    "ocr": {"enabled": true}
  },
  "file_size": 1048576,
  "created_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:00:30Z"
}
```

---

## Load Document from History

```http
GET /api/history/{job_id}/load
```

Load a previously converted document from history and return it as a conversion result. This endpoint loads the `DoclingDocument` from the stored JSON file and returns it in the same format as a fresh conversion result.

### Path Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `job_id` | string | Yes | The job identifier (must match `[A-Za-z0-9_-]+`) |

### Response

Returns a `ConversionResult` object matching the format of a fresh conversion:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "document": {
    "title": "My Document",
    "content": "...",
    "metadata": {...}
  },
  "formats_available": ["markdown", "html", "json"],
  "images_count": 5,
  "tables_count": 2,
  "preview": "# Document content preview..."
}
```

### Error Responses

**404 Not Found**: History entry does not exist
```json
{
  "error": "History entry {job_id} not found"
}
```

**400 Bad Request**: Conversion not completed
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Conversion not completed"
}
```

### Notes

- Only works for completed conversions
- If the stored document JSON file is unavailable, the endpoint will attempt to reconstruct the result from output files
- Documents are automatically stored after each successful conversion
- The `document_json_path` field in history entries indicates where the document JSON is stored

---

## Reconcile History from Disk

```http
POST /api/history/reconcile
```

Scans the output directory for conversion outputs that exist on disk but have no database entry (e.g. after DB loss or restart). Creates missing history entries so they appear in the UI and can be reloaded.

Reconciliation also runs automatically on application startup.

### Response

```json
{
  "message": "Reconciled 3 entries from disk",
  "added_count": 3,
  "added_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ]
}
```

### Notes

- Only output directories with valid UUID names and at least one output file (`.md`, `.html`, `.json`, or `.document.json`) are reconciled
- Entries already in the database are skipped

---

## Generate Chunks

```http
POST /api/history/{job_id}/generate-chunks
```

Generate RAG chunks for a completed document on demand. Loads the DoclingDocument from disk, applies current chunking settings, and returns the generated chunks. Saves chunks to disk for download.

### Response

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": [
    {
      "id": 1,
      "text": "Chunk content...",
      "meta": { "page": 1, "headings": ["Section Title"] }
    }
  ],
  "count": 42
}
```

**404 Not Found**: History entry or document not found

---

## Delete History Entry

```http
DELETE /api/history/{job_id}
```

### Response

```json
{
  "message": "Entry deleted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Get History Statistics

```http
GET /api/history/stats
```

### Response

Returns conversion statistics, storage usage, and queue depth. The `conversions` object includes extended metrics when available.

```json
{
  "conversions": {
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
    },
    "avg_processing_seconds": 12.5,
    "ocr_backend_breakdown": {
      "easyocr": 80,
      "ocrmac": 50,
      "tesseract": 20
    },
    "output_format_breakdown": {
      "markdown": 150
    },
    "performance_device_breakdown": {
      "auto": 120,
      "cpu": 30
    },
    "chunking_enabled_count": 25,
    "error_category_breakdown": {
      "ocr": 2,
      "other": 3
    },
    "source_type_breakdown": {
      "upload": 100,
      "url": 30,
      "batch": 20
    }
  },
  "storage": {
    "uploads": { "count": 10, "size_bytes": 1048576, "size_mb": 1.0 },
    "outputs": { "count": 140, "size_bytes": 52428800, "size_mb": 50.0 },
    "total_size_mb": 51.0
  },
  "queue_depth": 2
}
```

---

## Search History

```http
GET /api/history/search
```

### Query Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `limit` | int | No | Maximum results (default: 20) |

### Response

```json
{
  "entries": [...],
  "query": "invoice",
  "count": 5
}
```

---

## Export History

```http
GET /api/history/export
```

**Response**: JSON file download with all history entries

---

## Clear All History

```http
DELETE /api/history
```

### Response

```json
{
  "message": "All history entries deleted",
  "count": 150
}
```

