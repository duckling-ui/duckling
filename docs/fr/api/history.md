# API de l'historique

Endpoints pour accéder à l'historique des conversions.

## Obtenir l'historique des conversions

```http
GET /api/history
```

### Paramètres de requête

| Nom | Type | Par défaut | Description |
|------|------|-----------|-------------|
| `limit` | int | 50 | Nombre maximum d'entrées à retourner |
| `offset` | int | 0 | Nombre d'entrées à ignorer |
| `status` | string | - | Filtrer par statut |

### Réponse

```json
{
  "entries": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document_abc123.pdf",
      "original_filename": "My Document.pdf",
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

## Obtenir l'historique récent

```http
GET /api/history/recent
```

### Paramètres de requête

| Nom | Type | Par défaut | Description |
|------|------|-----------|-------------|
| `limit` | int | 10 | Nombre maximum d'entrées à retourner |

---

## Obtenir une entrée d'historique

```http
GET /api/history/{job_id}
```

### Réponse

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document_abc123.pdf",
  "original_filename": "My Document.pdf",
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

## Charger un document depuis l'historique

```http
GET /api/history/{job_id}/load
```

Charge un document précédemment converti depuis l'historique et le retourne comme un résultat de conversion. Cet endpoint charge le `DoclingDocument` depuis le fichier JSON stocké et le retourne dans le même format qu'un résultat de conversion frais.

### Paramètres de chemin

| Nom | Type | Requis | Description |
|------|------|--------|-------------|
| `job_id` | string | Oui | L'identifiant du job |

### Réponse

Retourne un objet `ConversionResult` correspondant au format d'une conversion fraîche :

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "document": {
    "title": "Mon Document",
    "content": "...",
    "metadata": {...}
  },
  "formats_available": ["markdown", "html", "json"],
  "images_count": 5,
  "tables_count": 2,
  "preview": "# Aperçu du contenu du document..."
}
```

### Réponses d'erreur

**404 Not Found**: L'entrée d'historique n'existe pas
```json
{
  "error": "History entry {job_id} not found"
}
```

**400 Bad Request**: Conversion non terminée
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Conversion not completed"
}
```

### Notes

- Ne fonctionne que pour les conversions terminées
- Si le fichier JSON du document stocké n'est pas disponible, l'endpoint tentera de reconstruire le résultat à partir des fichiers de sortie
- Les documents sont automatiquement stockés après chaque conversion réussie
- Le champ `document_json_path` dans les entrées d'historique indique où le JSON du document est stocké

---

## Supprimer une entrée d'historique

```http
DELETE /api/history/{job_id}
```

### Réponse

```json
{
  "message": "Entry deleted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Obtenir les statistiques de l'historique

```http
GET /api/history/stats
```

### Réponse

```json
{
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
  }
}
```

---

## Rechercher dans l'historique

```http
GET /api/history/search
```

### Paramètres de requête

| Nom | Type | Requis | Description |
|------|------|--------|-------------|
| `q` | string | Oui | Requête de recherche |
| `limit` | int | Non | Résultats maximum (par défaut : 20) |

### Réponse

```json
{
  "entries": [...],
  "query": "invoice",
  "count": 5
}
```

---

## Exporter l'historique

```http
GET /api/history/export
```

**Réponse** : Téléchargement d'un fichier JSON avec toutes les entrées d'historique

---

## Effacer tout l'historique

```http
DELETE /api/history
```

### Réponse

```json
{
  "message": "All history entries deleted",
  "count": 150
}
```
