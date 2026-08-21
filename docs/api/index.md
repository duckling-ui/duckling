# API Reference

Complete API documentation for the Duckling backend.

## Base URL

```
http://localhost:5001/api
```

## Authentication

When `DUCKLING_API_KEY` is set (environment variable or [server config file](../deployment/server-config.md)), all `/api/*` routes require the header:

```http
X-Api-Key: your-api-key
```

Exceptions: `/api/health` and embedded docs routes under `/api/docs/site`.

The React UI reads `VITE_API_KEY` at build time and sends `X-Api-Key` automatically.

When no API key is configured, the API remains open on the local network — restrict access with a reverse proxy in production.

## Sections

<div class="grid cards" markdown>

-   :material-file-document-multiple:{ .lg .middle } __Conversion__

    ---

    Upload and convert documents

    [:octicons-arrow-right-24: Conversion API](conversion.md)

-   :material-cog:{ .lg .middle } __Settings__

    ---

    Get and update configuration

    [:octicons-arrow-right-24: Settings API](settings.md)

-   :material-history:{ .lg .middle } __History__

    ---

    Access conversion history

    [:octicons-arrow-right-24: History API](history.md)

</div>

## Quick Reference

### Conversion Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/convert` | POST | Upload and convert a document |
| `/convert/batch` | POST | Batch convert multiple documents |
| `/convert/url` | POST | Convert a document from URL |
| `/convert/url/batch` | POST | Batch convert from URLs |
| `/convert/batch/connectors` | POST | Connector-based batch request (validation; worker integration for execution) |
| `/convert/{job_id}/status` | GET | Get conversion status |
| `/convert/{job_id}/result` | GET | Get conversion result |
| `/convert/{job_id}/images` | GET | List extracted images |
| `/convert/{job_id}/images/{id}` | GET | Download extracted image |
| `/convert/{job_id}/tables` | GET | List extracted tables |
| `/convert/{job_id}/tables/{id}/csv` | GET | Download table as CSV |
| `/convert/{job_id}/chunks` | GET | Get document chunks |
| `/export/{job_id}/{format}` | GET | Download converted file |

### Settings Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/settings` | GET/PUT | Get/update all settings |
| `/settings/reset` | POST | Reset to defaults |
| `/settings/formats` | GET | List supported formats |
| `/settings/ocr` | GET/PUT | OCR settings |
| `/settings/tables` | GET/PUT | Table settings |
| `/settings/images` | GET/PUT | Image settings |
| `/settings/performance` | GET/PUT | Performance settings |
| `/settings/chunking` | GET/PUT | Chunking settings (hybrid/hierarchical) |
| `/settings/pipeline` | GET/PUT | Pipeline kind (standard/vlm/asr) |
| `/settings/pdf` | GET/PUT | PDF backend and export options |
| `/settings/enrichment` | GET/PUT | Enrichment toggles and model status |

### History Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/history` | GET | List conversion history |
| `/history/{job_id}` | GET | Get history entry |
| `/history/stats` | GET | Get conversion statistics |
| `/history/search` | GET | Search history |

## Health Check

```http
GET /health
```

**Response**

```json
{
  "status": "healthy",
  "service": "duckling-backend"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 202 | Accepted (async operation started) |
| 400 | Bad Request (invalid input) |
| 404 | Not Found |
| 413 | Payload Too Large |
| 500 | Internal Server Error |

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider adding rate limiting middleware.

## CORS

The API allows cross-origin requests from the configured frontend origin (default: `http://localhost:3000`).

