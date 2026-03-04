# Référence API

Complete API documentation for the Duckling backend.

## Base URL

```
http://localhost:5001/api
```

## Authentication

Currently, the API does not require authentication. For production deployments, consider adding authentication middleware.

## Sections

<div class="grid cards" markdown>

-   :material-file-document-multiple:{ .lg .middle } __Conversion__

    ---

    Upload et convert documents

    [:octicons-arrow-right-24: Conversion API](conversion.md)

-   :material-cog:{ .lg .middle } __Paramètres__

    ---

    Get et update configuration

    [:octicons-arrow-right-24: Paramètres API](settings.md)

-   :material-history:{ .lg .middle } __History__

    ---

    Access conversion history

    [:octicons-arrow-right-24: History API](history.md)

</div>

## Référence rapide

### Conversion Endpoints

| Endpoint | Méthode | Description |
|----------|--------|-------------|
| `/convert` | POST | Télécharger et convertir un document |
| `/convert/batch` | POST | Batch convert multiple documents |
| `/convert/{job_id}/status` | GET | Get conversion status |
| `/convert/{job_id}/result` | GET | Get conversion result |
| `/convert/{job_id}/images` | GET | List extracted images |
| `/convert/{job_id}/images/{id}` | GET | Télécharger extracted image |
| `/convert/{job_id}/tables` | GET | List extracted tables |
| `/convert/{job_id}/tables/{id}/csv` | GET | Télécharger table as CSV |
| `/convert/{job_id}/chunks` | GET | Get document chunks |
| `/export/{job_id}/{format}` | GET | Télécharger converted file |

### Paramètres Endpoints

| Endpoint | Méthode | Description |
|----------|--------|-------------|
| `/settings` | GET/PUT | Get/update all settings |
| `/settings/reset` | POST | Reset to defaults |
| `/settings/formats` | GET | List supported formats |
| `/settings/ocr` | GET/PUT | OCR settings |
| `/settings/tables` | GET/PUT | Table settings |
| `/settings/images` | GET/PUT | Image settings |
| `/settings/performance` | GET/PUT | Performances settings |
| `/settings/chunking` | GET/PUT | Chunking settings |

### History Endpoints

| Endpoint | Méthode | Description |
|----------|--------|-------------|
| `/history` | GET | List conversion history |
| `/history/{job_id}` | GET | Get history entry |
| `/history/stats` | GET | Get conversion statistics |
| `/history/search` | GET | Search history |

## Health Check

```http
GET /health
```

**Réponse**

```json
{
  "status": "healthy",
  "service": "duckling-backend"
}
```

## Error Réponses

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

