# Configuración del servidor

Ajustes de despliegue de Duckling: clave API, motor de orquestación, registros estructurados y listas de conectores. Separados de los ajustes de conversión por sesión (UI/API `/api/settings`).

Referencia completa (inglés): [Server Configuration](../../deployment/server-config.md).

## Variables de entorno clave

| Variable | Descripción |
|----------|-------------|
| `DUCKLING_CONFIG_FILE` | Ruta a archivo JSON/YAML |
| `DUCKLING_API_KEY` | Requiere `X-Api-Key` en `/api/*` (excepto health/docs) |
| `DUCKLING_LOG_FORMAT` | `text` o `json` |
| `DUCKLING_ENGINE_KIND` | `local`, `rq` o `ray` |
| `DUCKLING_RQ_REDIS_URL` | URL Redis para modo RQ |

## Orquestación

| Modo | Comportamiento |
|------|----------------|
| **local** (predeterminado) | Conversiones en el proceso API |
| **rq** / **ray** | Adaptadores presentes; ejecución distribuida vía workers |

Compose define servicios `redis` y `rq-worker`. Ray/jobkit: opcional en `backend/requirements-orchestration.txt`.

Ver también [Escalado](scaling.md), [Seguridad](security.md), [API de conversión](../api/conversion.md#connector-batch-endpoint).
