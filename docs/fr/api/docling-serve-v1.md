# API docling-serve `/v1`

Duckling intègre [docling-serve](https://github.com/docling-project/docling-serve) et expose l’**OpenAPI `/v1` upstream** sur le même hôte que `/api/*`.

- URL de base : `http://localhost:5001/v1/...`
- Documentation interactive : `/docs`, schéma : `/openapi-3.0.json`
- Authentification : `DUCKLING_API_KEY` est mappé vers `DOCLING_SERVE_API_KEY` (`X-Api-Key`)
- Optionnel : `DUCKLING_USE_DOCLING_SERVE_ENGINE=true` pour `/api/convert` via docling-serve

Voir aussi [Configuration serveur](../deployment/server-config.md) (en).
