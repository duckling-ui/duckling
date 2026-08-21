# Conversion API

Endpoints for uploading and converting documents.

## Parity-oriented job options

Conversion endpoints accept optional per-job overrides in the JSON `settings` payload (multipart field or JSON body):

| Field | Type | Description |
|-------|------|-------------|
| `page_range` | `[start, end]` | 1-based inclusive PDF page range (also available in the UI drop zone) |
| `to_formats` | `string[]` | Limit exports for this job, e.g. `["markdown", "yaml", "doclang"]` |

Allowed `to_formats` values match server output formats: `markdown`, `html`, `json`, `text`, `doctags`, `doclang`, `dclx`, `yaml`, `html_split_page`, `vtt`, `document_tokens`, and `chunks` (when chunking is enabled).

### Example with page range and formats

```bash
curl -X POST http://localhost:5001/api/convert \
  -H "X-Api-Key: YOUR_KEY" \
  -F "file=@report.pdf" \
  -F 'settings={"page_range":[1,10],"to_formats":["markdown","yaml"]}'
```

When `DUCKLING_API_KEY` is set, include `X-Api-Key` on all conversion requests.

## Connector batch endpoint {#connector-batch-endpoint}

Enterprise workflow integration endpoint:

```http
POST /api/convert/batch/connectors
Content-Type: application/json
```

### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sources` | array | Yes | Non-empty list of connector source descriptors |
| `target` | object | Yes | Must include `kind` (target connector type) |
| `options` | object | No | Connector-specific options |

### Example

```json
{
  "sources": [{"kind": "filesystem", "path": "/data/inbox/doc.pdf"}],
  "target": {"kind": "filesystem", "path": "/data/out"},
  "options": {}
}
```

### Response (202 Accepted)

```json
{
  "status": "accepted",
  "message": "Connector batch request accepted",
  "sources_count": 1,
  "target_kind": "filesystem",
  "note": "Connector execution requires RQ/Ray worker integration."
}
```

The endpoint validates payload shape today. Full connector execution requires distributed worker integration — see [Server Configuration](../deployment/server-config.md) and [Scaling](../deployment/scaling.md).

---

## Upload and Convert Single Document

```http
POST /api/convert
Content-Type: multipart/form-data
```

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file` | File | Yes | Document to convert |
| `settings` | JSON string | No | Conversion settings override |

### Example Request

```bash
curl -X POST http://localhost:5001/api/convert \
  -F "file=@document.pdf" \
  -F 'settings={"ocr":{"enabled":true,"language":"en"}}'
```

### Response (202 Accepted)

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

## Batch Convert Multiple Documents

```http
POST /api/convert/batch
Content-Type: multipart/form-data
```

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `files` | File[] | Yes | Documents to convert (repeat the `files` field for each part). Folder uploads from the UI send the same shape: one multipart part per file after the browser expands the directory. |
| `settings` | JSON string | No | Conversion settings override |

**Supported types:** Each filename must have an extension allowed by the server (see deployment `ALLOWED_EXTENSIONS`). Unsupported parts are not converted; they appear in the response with `"status": "rejected"`. If **every** part is unsupported (or otherwise yields no conversion), the API returns **400** with an `error` message and the per-file `jobs` list.

**Request size:** The entire multipart body must be within `MAX_CONTENT_LENGTH` (default 100MB for the whole request), not per file. Large folders may need to be split into several batch requests.

### Example Request

```bash
curl -X POST http://localhost:5001/api/convert/batch \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "files=@image.png"
```

### Response (202 Accepted)

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

### Response (400 Bad Request)

Returned when no conversion jobs are started (for example, every file has a disallowed extension):

```json
{
  "error": "No supported files to convert",
  "jobs": [
    {
      "filename": "readme.exe",
      "status": "rejected",
      "error": "File type not allowed"
    }
  ],
  "total": 1
}
```

---

## Convert Document from URL

```http
POST /api/convert/url
Content-Type: application/json
```

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `url` | string | Yes | URL of the document to convert |
| `settings` | object | No | Conversion settings override |

### Example Request

```bash
curl -X POST http://localhost:5001/api/convert/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/document.pdf",
    "settings": {"ocr": {"enabled": true}}
  }'
```

### Response (202 Accepted)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "source_url": "https://example.com/document.pdf",
  "input_format": "pdf",
  "status": "processing",
  "message": "Conversion started"
}
```

---

## Batch Convert Documents from URLs

```http
POST /api/convert/url/batch
Content-Type: application/json
```

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `urls` | string[] | Yes | Array of URLs to convert |
| `settings` | object | No | Conversion settings override |

### Example Request

```bash
curl -X POST http://localhost:5001/api/convert/url/batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/doc1.pdf",
      "https://example.com/doc2.docx",
      "https://example.com/page.html"
    ]
  }'
```

### Response (202 Accepted)

```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440001",
      "url": "https://example.com/doc1.pdf",
      "filename": "doc1.pdf",
      "input_format": "pdf",
      "status": "processing"
    },
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440002",
      "url": "https://example.com/doc2.docx",
      "filename": "doc2.docx",
      "input_format": "docx",
      "status": "processing"
    },
    {
      "url": "https://example.com/invalid",
      "status": "rejected",
      "error": "File type not allowed"
    }
  ],
  "total": 3,
  "message": "Started 2 conversions"
}
```

---

## Get Conversion Status

```http
GET /api/convert/{job_id}/status
```

### Response (Processing)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "message": "Analyzing document with OCR (easyocr, en)..."
}
```

### Response (Completed)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "message": "Conversion completed successfully",
  "confidence": 0.92,
  "formats_available": ["markdown", "html", "json", "text", "doctags", "doclang"],
  "images_count": 3,
  "tables_count": 2,
  "chunks_count": 0,
  "preview": "# Document Title\n\nFirst paragraph..."
}
```

### Response (Failed)

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

## Get Conversion Result

```http
GET /api/convert/{job_id}/result
```

### Response

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "confidence": 0.92,
  "formats_available": ["markdown", "html", "json", "text", "doctags", "doclang", "document_tokens"],
  "result": {
    "markdown_preview": "# Document Title\n\nContent preview...",
    "formats_available": ["markdown", "html", "json", "text", "doctags", "doclang"],
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

## Get Extracted Images

```http
GET /api/convert/{job_id}/images
```

### Response

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

## Download Extracted Image

```http
GET /api/convert/{job_id}/images/{image_id}
```

**Response**: Binary image file (PNG)

---

## Get Extracted Tables

```http
GET /api/convert/{job_id}/tables
```

### Response

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

## Download Table as CSV

```http
GET /api/convert/{job_id}/tables/{table_id}/csv
```

**Response**: CSV file

---

## Download Table as Image

```http
GET /api/convert/{job_id}/tables/{table_id}/image
```

**Response**: Binary image file (PNG)

---

## Get Document Chunks

```http
GET /api/convert/{job_id}/chunks
```

### Response

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

## Export Document

```http
GET /api/export/{job_id}/{format}
```

### Supported Formats

- `markdown`
- `html`
- `json`
- `text`
- `doctags`
- `doclang` — DocLang XML (`.dclg.xml`, `application/xml`); see [Supported formats — DocLang](../user-guide/formats.md#doclang-dclgxml)
- `document_tokens`
- `chunks`

**Response**: File download with appropriate MIME type

Example:

```bash
curl -OJ http://localhost:5001/api/export/{job_id}/doclang
```

---

## Delete Job

```http
DELETE /api/convert/{job_id}
```

### Response

```json
{
  "message": "Job 550e8400-e29b-41d4-a716-446655440000 deleted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

