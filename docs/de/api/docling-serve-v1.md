# docling-serve `/v1` API

Duckling bindet [docling-serve](https://github.com/docling-project/docling-serve) ein und stellt die **upstream `/v1` OpenAPI** auf demselben Port wie `/api/*` bereit.

- Basis-URL: `http://localhost:5001/v1/...`
- Interaktive Doku: `/docs`, Schema: `/openapi-3.0.json`
- Authentifizierung: `DUCKLING_API_KEY` wird zu `DOCLING_SERVE_API_KEY` gemappt (`X-Api-Key`)
- Optional: `DUCKLING_USE_DOCLING_SERVE_ENGINE=true` leitet `/api/convert` über docling-serve

Siehe auch [Server-Konfiguration](../deployment/server-config.md) (en).
