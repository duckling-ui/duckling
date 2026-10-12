# Server-Konfiguration

Bereitstellungs-Einstellungen für Duckling: API-Schlüssel, Orchestrierungs-Engine, strukturierte Logs und Connector-Allowlists. Getrennt von Sitzungs-Konvertierungseinstellungen in der UI/API (`/api/settings`).

Siehe die vollständige englische Referenz in [Server Configuration](../../deployment/server-config.md) (gleiche Pfade und Variablen).

## Wichtige Umgebungsvariablen

| Variable | Beschreibung |
|----------|--------------|
| `DUCKLING_CONFIG_FILE` | Pfad zu JSON/YAML-Serverkonfiguration |
| `DUCKLING_API_KEY` | Erfordert `X-Api-Key` auf `/api/*` (außer Health/Docs) |
| `DUCKLING_LOG_FORMAT` | `text` oder `json` |
| `DUCKLING_ENGINE_KIND` | `local`, `rq` oder `ray` |
| `DUCKLING_RQ_REDIS_URL` | Redis-URL für RQ-Modus |

## Orchestrierung

| Modus | Verhalten |
|-------|-----------|
| **local** (Standard) | Konvertierungen im API-Prozess; Gunicorn **1** Worker (Issue #67) |
| **rq** / **ray** | Adapter vorhanden; verteilte Ausführung erfordert Worker-Integration |

Compose definiert `redis`- und `rq-worker`-Dienste. Ray/jobkit: optional `backend/requirements-orchestration.txt`. Frontend-tmpfs für nginx muss UID/GID **1000** besitzen.

Weitere Details: [Skalierung](scaling.md), [Sicherheit](security.md), [Konvertierungs-API](../api/conversion.md#connector-batch-endpoint).
