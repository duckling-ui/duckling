# docling-serve upgrade playbook

Use this checklist when bumping `docling-serve` in `backend/requirements-docling-serve.txt`.

## 1. Pin and install

```bash
cd backend
pip install -r requirements.txt -r requirements-docling-serve.txt
```

## 2. Contract tests

```bash
pytest tests/test_docling_serve_contract.py -v
pytest backend/tests/test_settings_mapper.py -v
```

Update `tests/fixtures/docling_serve_paths.json` if upstream adds/removes `/v1` routes.

## 3. OpenAPI diff

```bash
curl -s http://localhost:5001/openapi-3.0.json | jq '.paths | keys[]' | sort
```

Compare against the previous release artifact or docling-serve tag.

## 4. Docker / Trivy

```bash
docker compose build backend
# Run publish rehearsal or local Trivy scan before tagging
```

## 5. Smoke test

1. `GET /health` and `GET /api/health`
2. `POST /v1/convert/file/async` with a small PDF
3. Duckling UI upload with `DUCKLING_USE_DOCLING_SERVE_ENGINE=true`

## 6. Document

- [CHANGELOG.md](../../CHANGELOG.md) and [docs/changelog.md](../changelog.md)
- [docs/api/docling-serve-v1.md](../api/docling-serve-v1.md) if endpoint table changed
