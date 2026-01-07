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
  "settings": {
    "ocr": {"enabled": true}
  },
  "file_size": 1048576,
  "created_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:00:30Z"
}
```

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

