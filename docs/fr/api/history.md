# API Historique

Points de terminaison pour accéder à l’historique des conversions.

## Obtenir l’historique des conversions

```http
GET /api/history
```

### Paramètres de requête

| Nom | Type | Défaut | Description |
|-----|------|--------|-------------|
| `limit` | int | 50 | Nombre maximal d’entrées à renvoyer |
| `offset` | int | 0 | Nombre d’entrées à ignorer |
| `status` | string | - | Filtrer par statut |

### Réponse

```json
{
  "entries": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document_abc123.pdf",
      "original_filename": "Mon document.pdf",
      "input_format": "pdf",
      "status": "completed",
      "confidence": 0.92,
      "file_size": 1048576,
      "created_at": "2024-01-15T10:00:00Z",
      "completed_at": "2024-01-15T10:00:30Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

## Obtenir l’historique récent

```http
GET /api/history/recent
```

### Paramètres de requête

| Nom | Type | Défaut | Description |
|-----|------|--------|-------------|
| `limit` | int | 10 | Nombre maximal d’entrées à renvoyer |

---

## Obtenir une entrée d’historique

```http
GET /api/history/{job_id}
```

### Réponse

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document_abc123.pdf",
  "original_filename": "Mon document.pdf",
  "input_format": "pdf",
  "status": "completed",
  "confidence": 0.92,
  "error_message": null,
  "output_path": "/outputs/550e8400.../document.md",
  "document_json_path": "/outputs/550e8400.../document.json",
  "settings": {
    "ocr": {"enabled": true}
  },
  "file_size": 1048576,
  "created_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:00:30Z"
}
```

---

## Charger un document depuis l’historique

```http
GET /api/history/{job_id}/load
```

Charge un document précédemment converti depuis l’historique et le renvoie comme résultat de conversion. Ce point de terminaison charge le `DoclingDocument` depuis le fichier JSON stocké et le renvoie au même format qu’un résultat de conversion tout juste produit.

### Paramètres de chemin

| Nom | Type | Obligatoire | Description |
|-----|------|-------------|-------------|
| `job_id` | string | Oui | Identifiant du travail (doit correspondre à `[A-Za-z0-9_-]+`) |

### Réponse

Renvoie un objet `ConversionResult` au même format qu’une conversion fraîche :

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "document": {
    "title": "Mon document",
    "content": "...",
    "metadata": {...}
  },
  "formats_available": ["markdown", "html", "json"],
  "images_count": 5,
  "tables_count": 2,
  "preview": "# Aperçu du contenu du document..."
}
```

### Réponses d’erreur

**404 Not Found** : l’entrée d’historique n’existe pas
```json
{
  "error": "Entrée d’historique {job_id} introuvable"
}
```

**400 Bad Request** : conversion non terminée
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Conversion non terminée"
}
```

### Notes

- Ne fonctionne que pour les conversions terminées
- Si le fichier JSON du document stocké est indisponible, le point de terminaison tentera de reconstruire le résultat à partir des fichiers de sortie
- Les documents sont automatiquement stockés après chaque conversion réussie
- Le champ `document_json_path` dans les entrées d’historique indique où le JSON du document est stocké

---

## Réconcilier l’historique avec le disque

```http
POST /api/history/reconcile
```

Parcourt le répertoire de sortie à la recherche de sorties de conversion présentes sur le disque mais sans entrée en base (par ex. après perte de la base ou redémarrage). Crée les entrées d’historique manquantes pour qu’elles apparaissent dans l’interface et puissent être rechargées.

La réconciliation s’exécute aussi automatiquement au démarrage de l’application.

### Réponse

```json
{
  "message": "3 entrées réconciliées depuis le disque",
  "added_count": 3,
  "added_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ]
}
```

### Notes

- Seuls les répertoires de sortie dont le nom est un UUID valide et qui contiennent au moins un fichier de sortie (`.md`, `.html`, `.json` ou `.document.json`) sont réconciliés
- Les entrées déjà présentes en base sont ignorées

---

## Générer des segments (chunks)

```http
POST /api/history/{job_id}/generate-chunks
```

Génère à la demande des segments RAG pour un document terminé. Charge le `DoclingDocument` depuis le disque, applique les paramètres de découpage actuels et renvoie les segments générés. Enregistre les segments sur le disque pour téléchargement.

### Réponse

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": [
    {
      "id": 1,
      "text": "Contenu du segment...",
      "meta": { "page": 1, "headings": ["Titre de section"] }
    }
  ],
  "count": 42
}
```

**404 Not Found** : entrée d’historique ou document introuvable

---

## Supprimer une entrée d’historique

```http
DELETE /api/history/{job_id}
```

### Réponse

```json
{
  "message": "Entrée supprimée",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Obtenir les statistiques d’historique

```http
GET /api/history/stats
```

### Réponse

Renvoie des statistiques de conversion, l’utilisation du stockage et la profondeur de la file. L’objet `conversions` inclut des métriques étendues lorsqu’elles sont disponibles.

```json
{
  "conversions": {
    "total": 150,
    "completed": 142,
    "failed": 5,
    "pending": 2,
    "processing": 1,
    "success_rate": 94.7,
    "format_breakdown": {
      "pdf": 100,
      "docx": 30,
      "image": 20
    },
    "avg_processing_seconds": 12.5,
    "ocr_backend_breakdown": {
      "easyocr": 80,
      "ocrmac": 50,
      "tesseract": 20
    },
    "output_format_breakdown": {
      "markdown": 150
    },
    "performance_device_breakdown": {
      "auto": 120,
      "cpu": 30
    },
    "chunking_enabled_count": 25,
    "error_category_breakdown": {
      "ocr": 2,
      "other": 3
    },
    "source_type_breakdown": {
      "upload": 100,
      "url": 30,
      "batch": 20
    }
  },
  "storage": {
    "uploads": { "count": 10, "size_bytes": 1048576, "size_mb": 1.0 },
    "outputs": { "count": 140, "size_bytes": 52428800, "size_mb": 50.0 },
    "total_size_mb": 51.0
  },
  "queue_depth": 2
}
```

---

## Rechercher dans l’historique

```http
GET /api/history/search
```

### Paramètres de requête

| Nom | Type | Obligatoire | Description |
|-----|------|-------------|-------------|
| `q` | string | Oui | Requête de recherche |
| `limit` | int | Non | Nombre maximal de résultats (défaut : 20) |

### Réponse

```json
{
  "entries": [...],
  "query": "facture",
  "count": 5
}
```

---

## Exporter l’historique

```http
GET /api/history/export
```

**Réponse** : téléchargement d’un fichier JSON contenant toutes les entrées d’historique

---

## Effacer tout l’historique

```http
DELETE /api/history
```

### Réponse

```json
{
  "message": "Toutes les entrées d’historique ont été supprimées",
  "count": 150
}
```
