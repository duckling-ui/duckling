# API docling-serve `/v1`

Duckling integra [docling-serve](https://github.com/docling-project/docling-serve) y expone la **OpenAPI `/v1` upstream** en el mismo host que `/api/*`.

- URL base: `http://localhost:5001/v1/...`
- Documentación interactiva: `/docs`, esquema: `/openapi-3.0.json`
- Autenticación: `DUCKLING_API_KEY` se mapea a `DOCLING_SERVE_API_KEY` (`X-Api-Key`)
- Opcional: `DUCKLING_USE_DOCLING_SERVE_ENGINE=true` para `/api/convert` vía docling-serve

Ver también [Configuración del servidor](../deployment/server-config.md) (en).
