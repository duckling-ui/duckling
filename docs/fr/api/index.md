# Référence API

Documentation complète de l’API backend Duckling.

## URL de base

```
http://localhost:5001/api
```

## Authentification

Si `DUCKLING_API_KEY` est défini (variable d'environnement ou [fichier de configuration serveur](../deployment/server-config.md)), toutes les routes `/api/*` sauf health et docs intégrées exigent :

```http
X-Api-Key: your-api-key
```

L'UI React lit `VITE_API_KEY` au build et envoie `X-Api-Key` automatiquement.

Sans clé API, l'API reste ouverte sur le réseau local — restreindre l'accès via reverse proxy en production.

## Sections

<div class="grid cards" markdown>

-   :material-file-document-multiple:{ .lg .middle } __Conversion__

    ---

    Téléverser et convertir des documents

    [:octicons-arrow-right-24: API de conversion](conversion.md)

-   :material-cog:{ .lg .middle } __Paramètres__

    ---

    Lire et mettre à jour la configuration

    [:octicons-arrow-right-24: API des paramètres](settings.md)

-   :material-history:{ .lg .middle } __Historique__

    ---

    Accéder à l’historique des conversions

    [:octicons-arrow-right-24: API d’historique](history.md)

</div>

## Référence rapide

### Points de terminaison de conversion

| Point de terminaison | Méthode | Description |
|----------|--------|-------------|
| `/convert` | POST | Téléverser et convertir un document |
| `/convert/batch` | POST | Convertir plusieurs documents par lot |
| `/convert/url` | POST | Convertir un document depuis une URL |
| `/convert/url/batch` | POST | Lot de conversions depuis des URLs |
| `/convert/batch/connectors` | POST | Requête batch connecteurs (validation ; workers pour exécution) |
| `/convert/{job_id}/status` | GET | Obtenir l’état de la conversion |
| `/convert/{job_id}/result` | GET | Obtenir le résultat de la conversion |
| `/convert/{job_id}/images` | GET | Lister les images extraites |
| `/convert/{job_id}/images/{id}` | GET | Télécharger une image extraite |
| `/convert/{job_id}/tables` | GET | Lister les tableaux extraits |
| `/convert/{job_id}/tables/{id}/csv` | GET | Télécharger un tableau au format CSV |
| `/convert/{job_id}/chunks` | GET | Obtenir les segments du document |
| `/export/{job_id}/{format}` | GET | Télécharger le fichier converti |

### Points de terminaison des paramètres

| Point de terminaison | Méthode | Description |
|----------|--------|-------------|
| `/settings` | GET/PUT | Lire/mettre à jour tous les paramètres |
| `/settings/reset` | POST | Réinitialiser aux valeurs par défaut |
| `/settings/formats` | GET | Lister les formats pris en charge |
| `/settings/ocr` | GET/PUT | Paramètres OCR |
| `/settings/tables` | GET/PUT | Paramètres des tableaux |
| `/settings/images` | GET/PUT | Paramètres des images |
| `/settings/performance` | GET/PUT | Paramètres de performance |
| `/settings/chunking` | GET/PUT | Découpage (hybride/hiérarchique) |
| `/settings/pipeline` | GET/PUT | Type de pipeline (standard/vlm/asr) |
| `/settings/pdf` | GET/PUT | Backend PDF et options d'export |
| `/settings/enrichment` | GET/PUT | Enrichissement et statut des modèles |

### Points de terminaison d’historique

| Point de terminaison | Méthode | Description |
|----------|--------|-------------|
| `/history` | GET | Lister l’historique des conversions |
| `/history/{job_id}` | GET | Obtenir une entrée d’historique |
| `/history/stats` | GET | Obtenir les statistiques de conversion |
| `/history/search` | GET | Rechercher dans l’historique |

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

## Réponses d’erreur

Tous les points de terminaison peuvent renvoyer des erreurs au format suivant :

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### Codes de statut HTTP

| Code | Description |
|------|-------------|
| 200 | Succès |
| 202 | Accepté (opération asynchrone démarrée) |
| 400 | Requête incorrecte (entrée invalide) |
| 404 | Non trouvé |
| 413 | Charge utile trop volumineuse |
| 500 | Erreur interne du serveur |

## Limitation du débit

Aucune limitation du débit n’est implémentée pour le moment. En production, envisagez d’ajouter un middleware de limitation.

## CORS

L’API autorise les requêtes cross-origin depuis l’origine du frontend configurée (par défaut : `http://localhost:3000`).
