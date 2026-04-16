# API de conversion

Points de terminaison pour téléverser et convertir des documents.

## Téléverser et convertir un document unique

```http
POST /api/convert
Content-Type: multipart/form-data
```

### Paramètres

| Nom | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `file` | Fichier | Oui | Document à convertir |
| `settings` | Chaîne JSON | Non | Surcharge des paramètres de conversion |

### Exemple de requête

```bash
curl -X POST http://localhost:5001/api/convert \
  -F "file=@document.pdf" \
  -F 'settings={"ocr":{"enabled":true,"language":"en"}}'
```

### Réponse (202 Accepted)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "input_format": "pdf",
  "status": "processing",
  "message": "Conversion started"
}
```

---

## Conversion par lot de plusieurs documents

```http
POST /api/convert/batch
Content-Type: multipart/form-data
```

### Paramètres

| Nom | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `files` | Fichier[] | Oui | Documents à convertir (répétez le champ `files` pour chaque partie). Les téléversements de dossiers depuis l’interface envoient la même forme : une partie multipart par fichier après que le navigateur ait développé le répertoire. |
| `settings` | Chaîne JSON | Non | Surcharge des paramètres de conversion |

**Types pris en charge :** Chaque nom de fichier doit avoir une extension autorisée par le serveur (voir `ALLOWED_EXTENSIONS` en déploiement). Les parties non prises en charge ne sont pas converties ; elles apparaissent dans la réponse avec `"status": "rejected"`. Si **toutes** les parties sont non prises en charge (ou ne donnent aucune conversion), l’API renvoie **400** avec un message `error` et la liste `jobs` par fichier.

**Taille de la requête :** L’ensemble du corps multipart doit respecter `MAX_CONTENT_LENGTH` (100 Mo par défaut pour toute la requête), et non par fichier. Les gros dossiers peuvent nécessiter plusieurs requêtes par lot.

### Exemple de requête

```bash
curl -X POST http://localhost:5001/api/convert/batch \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "files=@image.png"
```

### Réponse (202 Accepted)

```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440001",
      "filename": "doc1.pdf",
      "input_format": "pdf",
      "status": "processing"
    },
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440002",
      "filename": "doc2.pdf",
      "input_format": "pdf",
      "status": "processing"
    },
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440003",
      "filename": "image.png",
      "input_format": "image",
      "status": "processing"
    }
  ],
  "total": 3,
  "message": "Started 3 conversions"
}
```

### Réponse (400 Bad Request)

Renvoyée lorsqu’aucune tâche de conversion n’est démarrée (par exemple, si chaque fichier a une extension interdite) :

```json
{
  "error": "No supported files to convert",
  "jobs": [
    {
      "filename": "readme.exe",
      "status": "rejected",
      "error": "File type not allowed"
    }
  ],
  "total": 1
}
```

---

## Convertir un document à partir d’une URL

```http
POST /api/convert/url
Content-Type: application/json
```

### Paramètres

| Nom | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `url` | chaîne | Oui | URL du document à convertir |
| `settings` | objet | Non | Surcharge des paramètres de conversion |

### Exemple de requête

```bash
curl -X POST http://localhost:5001/api/convert/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/document.pdf",
    "settings": {"ocr": {"enabled": true}}
  }'
```

### Réponse (202 Accepted)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "source_url": "https://example.com/document.pdf",
  "input_format": "pdf",
  "status": "processing",
  "message": "Conversion started"
}
```

---

## Conversion par lot de documents à partir d’URL

```http
POST /api/convert/url/batch
Content-Type: application/json
```

### Paramètres

| Nom | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `urls` | chaîne[] | Oui | Tableau d’URL à convertir |
| `settings` | objet | Non | Surcharge des paramètres de conversion |

### Exemple de requête

```bash
curl -X POST http://localhost:5001/api/convert/url/batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/doc1.pdf",
      "https://example.com/doc2.docx",
      "https://example.com/page.html"
    ]
  }'
```

### Réponse (202 Accepted)

```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440001",
      "url": "https://example.com/doc1.pdf",
      "filename": "doc1.pdf",
      "input_format": "pdf",
      "status": "processing"
    },
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440002",
      "url": "https://example.com/doc2.docx",
      "filename": "doc2.docx",
      "input_format": "docx",
      "status": "processing"
    },
    {
      "url": "https://example.com/invalid",
      "status": "rejected",
      "error": "File type not allowed"
    }
  ],
  "total": 3,
  "message": "Started 2 conversions"
}
```

---

## Obtenir l’état d’une conversion

```http
GET /api/convert/{job_id}/status
```

### Réponse (en cours)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "message": "Analyzing document with OCR (easyocr, en)..."
}
```

### Réponse (terminée)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "message": "Conversion completed successfully",
  "confidence": 0.92,
  "formats_available": ["markdown", "html", "json", "text", "doctags"],
  "images_count": 3,
  "tables_count": 2,
  "chunks_count": 0,
  "preview": "# Titre du document\n\nPremier paragraphe…"
}
```

### Réponse (échec)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "progress": 0,
  "message": "Conversion failed: Invalid PDF format",
  "error": "Invalid PDF format"
}
```

---

## Obtenir le résultat d’une conversion

```http
GET /api/convert/{job_id}/result
```

### Réponse

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "confidence": 0.92,
  "formats_available": ["markdown", "html", "json", "text", "doctags", "document_tokens"],
  "result": {
    "markdown_preview": "# Titre du document\n\nAperçu du contenu…",
    "formats_available": ["markdown", "html", "json", "text", "doctags"],
    "page_count": 5,
    "images_count": 3,
    "tables_count": 2,
    "chunks_count": 0,
    "warnings": []
  },
  "images_count": 3,
  "tables_count": 2,
  "chunks_count": 0,
  "completed_at": "2024-01-15T10:30:00Z"
}
```

---

## Obtenir les images extraites

```http
GET /api/convert/{job_id}/images
```

### Réponse

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "images": [
    {
      "id": 1,
      "filename": "image_1.png",
      "path": "/outputs/job_id/images/image_1.png",
      "caption": "Figure 1 : schéma d’architecture",
      "label": "figure"
    },
    {
      "id": 2,
      "filename": "image_2.png",
      "path": "/outputs/job_id/images/image_2.png",
      "caption": "",
      "label": "picture"
    }
  ],
  "count": 2
}
```

---

## Télécharger une image extraite

```http
GET /api/convert/{job_id}/images/{image_id}
```

**Réponse :** fichier image binaire (PNG)

---

## Obtenir les tableaux extraits

```http
GET /api/convert/{job_id}/tables
```

### Réponse

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "tables": [
    {
      "id": 1,
      "label": "table",
      "caption": "Tableau 1 : données de ventes",
      "rows": [
        ["Produit", "T1", "T2", "T3", "T4"],
        ["Widget A", "100", "150", "200", "175"]
      ],
      "csv_path": "/outputs/job_id/tables/table_1.csv",
      "image_path": "/outputs/job_id/tables/table_1.png"
    }
  ],
  "count": 1
}
```

---

## Télécharger un tableau au format CSV

```http
GET /api/convert/{job_id}/tables/{table_id}/csv
```

**Réponse :** fichier CSV

---

## Télécharger un tableau en image

```http
GET /api/convert/{job_id}/tables/{table_id}/image
```

**Réponse :** fichier image binaire (PNG)

---

## Obtenir les fragments (chunks) du document

```http
GET /api/convert/{job_id}/chunks
```

### Réponse

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": [
    {
      "id": 1,
      "text": "Premier extrait de texte du document…",
      "meta": {
        "headings": ["Introduction"],
        "page": 1
      }
    },
    {
      "id": 2,
      "text": "Le deuxième extrait poursuit le contenu…",
      "meta": {
        "headings": ["Introduction", "Contexte"],
        "page": 1
      }
    }
  ],
  "count": 2
}
```

---

## Exporter le document

```http
GET /api/export/{job_id}/{format}
```

### Formats pris en charge

- `markdown`
- `html`
- `json`
- `text`
- `doctags`
- `document_tokens`
- `chunks`

**Réponse :** téléchargement de fichier avec le type MIME approprié

---

## Supprimer une tâche

```http
DELETE /api/convert/{job_id}
```

### Réponse

```json
{
  "message": "Job 550e8400-e29b-41d4-a716-446655440000 deleted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```
