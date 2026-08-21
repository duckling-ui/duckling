# Server Configuration

Deploy-time settings for Duckling: API key auth, orchestration engine, structured logging, and connector allowlists. These options are separate from per-session conversion settings in the UI/API (`/api/settings`).

## Configuration sources

Duckling merges settings in this order (later wins):

1. Built-in defaults in `backend/server_config.py`
2. **`DUCKLING_CONFIG_FILE`** — JSON or YAML file path
3. Environment variables (`DUCKLING_*`)

Session conversion settings (OCR, pipeline kind, chunking, etc.) remain in the database per user and are **not** loaded from the server config file.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DUCKLING_CONFIG_FILE` | *(unset)* | Path to JSON/YAML server config |
| `DUCKLING_API_KEY` | *(empty)* | When set, all `/api/*` routes except health/docs require `X-Api-Key` |
| `DUCKLING_LOG_FORMAT` | `text` | `text` or `json` (structured logs for production) |
| `DUCKLING_LOG_LEVEL` | `INFO` | Python log level |
| `DUCKLING_ENGINE_KIND` | `local` | `local`, `rq`, or `ray` (orchestration adapter selection) |
| `DUCKLING_RQ_REDIS_URL` | `redis://redis:6379/0` | Redis URL for RQ mode |
| `DUCKLING_RQ_QUEUE_NAME` | `convert` | RQ queue name |
| `DUCKLING_RQ_RESULTS_TTL` | `14400` | RQ result TTL (seconds) |
| `DUCKLING_RAY_ADDRESS` | *(empty)* | Ray cluster address when using Ray mode |
| `DUCKLING_ENABLE_REMOTE_SERVICES` | `false` | Allow remote service integrations (server flag) |
| `DUCKLING_ALLOW_CUSTOM_VLM_CONFIG` | `false` | Allow `pipeline.vlm_custom_config` dict in conversion settings |

Frontend clients can send the API key via build-time env `VITE_API_KEY`; the UI adds `X-Api-Key` on every request when set.

## Example config file

Save as `duckling-server.yaml` and point `DUCKLING_CONFIG_FILE` at it:

```yaml
api_key: "replace-with-long-random-key"
cors_origins:
  - "https://duckling.example.com"
engine:
  kind: local          # local | rq | ray
  rq_redis_url: redis://redis:6379/0
  rq_queue_name: convert
  rq_results_ttl: 14400
ray:
  address: ""          # e.g. ray://head:10001 when using Ray
logging:
  level: INFO
  format: json
connectors:
  allowed_source_types: []
  allowed_target_types: []
  allow_external_plugins: false
enable_remote_services: false
allow_custom_vlm_config: false
```

Equivalent JSON is supported when the file ends in `.json`.

## Orchestration modes

| Mode | Behavior today | Compose |
|------|----------------|---------|
| **`local`** (default) | Conversions run in-process on the API server (background thread queue) | API container only |
| **`rq`** | RQ adapter selected; falls back to local execution until worker integration is complete | `redis` + `rq-worker` services in `docker-compose.yml` |
| **`ray`** | Ray adapter selected; requires optional `backend/requirements-orchestration.txt` | Optional Ray cluster |

Install Ray/jobkit extras only when needed:

```bash
pip install -r backend/requirements.txt -r backend/requirements-orchestration.txt
```

See [Scaling](scaling.md) for topology and [Security](security.md) for API key hardening.

## Connector allowlists

The `connectors` block in the config file defines server-side allowlists for future connector plugins:

- `allowed_source_types` / `allowed_target_types` — restrict connector payload types
- `allow_external_plugins` — gate third-party connector modules (default `false`)

The batch connector API (`POST /api/convert/batch/connectors`) validates request shape today; distributed connector execution requires RQ/Ray worker integration. See [Conversion API](../api/conversion.md#connector-batch-endpoint).

## Production checklist

- [ ] Set `DUCKLING_API_KEY` (or `api_key` in config file) behind HTTPS
- [ ] Set `DUCKLING_LOG_FORMAT=json` and ship logs to your aggregator
- [ ] Restrict `cors_origins` to your frontend origin
- [ ] Keep `allow_custom_vlm_config` and `allow_external_plugins` off unless you trust all API callers
- [ ] Use `docker-compose.prod.yml` for hardened container defaults
