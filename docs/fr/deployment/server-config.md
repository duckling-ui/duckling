# Configuration serveur

Paramètres de déploiement Duckling : clé API, moteur d'orchestration, journaux structurés et listes autorisées pour connecteurs. Distincts des réglages de conversion par session (UI/API `/api/settings`).

Référence complète (anglais) : [Server Configuration](../../deployment/server-config.md).

## Variables d'environnement clés

| Variable | Description |
|----------|-------------|
| `DUCKLING_CONFIG_FILE` | Chemin vers un fichier JSON/YAML |
| `DUCKLING_API_KEY` | Exige `X-Api-Key` sur `/api/*` (sauf health/docs) |
| `DUCKLING_LOG_FORMAT` | `text` ou `json` |
| `DUCKLING_ENGINE_KIND` | `local`, `rq` ou `ray` |
| `DUCKLING_RQ_REDIS_URL` | URL Redis pour le mode RQ |

## Orchestration

| Mode | Comportement |
|------|--------------|
| **local** (défaut) | Conversions dans le processus API |
| **rq** / **ray** | Adaptateurs présents ; exécution distribuée via workers |

Compose inclut les services `redis` et `rq-worker`. Ray/jobkit : optionnel via `backend/requirements-orchestration.txt`.

Voir aussi [Mise à l'échelle](scaling.md), [Sécurité](security.md), [API Conversion](../api/conversion.md#connector-batch-endpoint).
