# docling-serve `/v1` API

Duckling embeds [docling-serve](https://github.com/docling-project/docling-serve) as a library and exposes the **exact upstream `/v1` OpenAPI** on the same port as Duckling's `/api/*` routes.

## Base URL

```
http://localhost:5001
```

Through the frontend nginx proxy (port 3000):

```
http://localhost:3000/v1/...
```

## Interactive documentation

| URL | Description |
|-----|-------------|
| `/docs` | Swagger UI (OpenAPI) |
| `/scalar` | Scalar API reference |
| `/openapi-3.0.json` | OpenAPI 3.0 schema |

## Authentication

When `DUCKLING_API_KEY` is set, docling-serve receives the same key via `DOCLING_SERVE_API_KEY` (mapped at startup). Send:

```http
X-Api-Key: your-api-key
```

## Core endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/convert/source` | POST | Convert from URL or base64 sources (sync) |
| `/v1/convert/file` | POST | Convert uploaded files (sync) |
| `/v1/convert/source/async` | POST | Async convert from sources |
| `/v1/convert/file/async` | POST | Async convert from files |
| `/v1/status/poll/{task_id}` | GET | Poll task status |
| `/v1/status/ws/{task_id}` | WebSocket | Task status stream |
| `/v1/result/{task_id}` | GET | Fetch completed result |
| `/v1/chunk/hybrid/{source\|file}` | POST | Chunk documents (hybrid) |
| `/v1/chunk/hierarchical/{source\|file}` | POST | Chunk documents (hierarchical) |
| `/health` | GET | Health check |
| `/ready` | GET | Readiness probe |
| `/version` | GET | docling-serve version |

See the live `/docs` page on your running instance for the authoritative schema.

## Example: async file conversion

```bash
curl -X POST "http://localhost:5001/v1/convert/file/async" \
  -H "X-Api-Key: YOUR_KEY" \
  -F "files=@document.pdf" \
  -F 'options={"to_formats":["markdown"]}'
```

Poll status:

```bash
curl "http://localhost:5001/v1/status/poll/TASK_ID"
```

Fetch result:

```bash
curl "http://localhost:5001/v1/result/TASK_ID"
```

## Duckling `/api` vs docling-serve `/v1`

| Surface | Purpose |
|---------|---------|
| `/v1/*` | Standard docling-serve contract for external integrators |
| `/api/*` | Duckling UI: history, settings, exports, embedded docs |

Optional: set `DUCKLING_USE_DOCLING_SERVE_ENGINE=true` to route `/api/convert` through docling-serve while still returning Duckling `job_id` to the UI. See [Server Configuration](../deployment/server-config.md).

## Runtime

Production Docker images run an ASGI composite app (`backend/asgi.py`):

- docling-serve FastAPI app at `/v1`, `/docs`, `/health`
- Duckling Flask app mounted at `/api`

Development:

```bash
cd backend
pip install -r requirements.txt -r requirements-docling-serve.txt
uvicorn asgi:app --host 0.0.0.0 --port 5001 --reload
```
