# History API

Endpoints for accessing conversion history.

## Get Conversion History

```http
GET /api/history
```

### Query Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | int | 50 | Maximum entries to return |
| `offset` | int | 0 | Number of entries to skip |
| `status` | string | - | Filter by status |

### Response

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

## Get Recent History

```http
GET /api/history/recent
```

### Query Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | int | 10 | Maximum entries to return |

---

## Get History Entry

```http
GET /api/history/{job_id}
```

### Response

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

## Dokument aus dem Verlauf laden

```http
GET /api/history/{job_id}/load
```

Lädt ein zuvor konvertiertes Dokument aus dem Verlauf und gibt es als Konvertierungsergebnis zurück. Dieser Endpunkt lädt das `DoclingDocument` aus der gespeicherten JSON-Datei und gibt es im gleichen Format wie ein frisches Konvertierungsergebnis zurück.

### Pfadparameter

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `job_id` | string | Ja | Die Job-Kennung (muss `[A-Za-z0-9_-]+` entsprechen) |

### Antwort

Gibt ein `ConversionResult`-Objekt zurück, das dem Format einer frischen Konvertierung entspricht:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "document": {
    "title": "Mein Dokument",
    "content": "...",
    "metadata": {...}
  },
  "formats_available": ["markdown", "html", "json"],
  "images_count": 5,
  "tables_count": 2,
  "preview": "# Dokumentinhalt-Vorschau..."
}
```

### Fehlerantworten

**404 Not Found**: Verlaufseintrag existiert nicht
```json
{
  "error": "History entry {job_id} not found"
}
```

**400 Bad Request**: Konvertierung nicht abgeschlossen
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Conversion not completed"
}
```

### Hinweise

- Funktioniert nur für abgeschlossene Konvertierungen
- Wenn die gespeicherte Dokument-JSON-Datei nicht verfügbar ist, versucht der Endpunkt, das Ergebnis aus den Ausgabedateien zu rekonstruieren
- Dokumente werden automatisch nach jeder erfolgreichen Konvertierung gespeichert
- Das Feld `document_json_path` in Verlaufseinträgen gibt an, wo das Dokument-JSON gespeichert ist

---

## Verlauf von Datenträger abgleichen

```http
POST /api/history/reconcile
```

Durchsucht das Ausgabeverzeichnis nach Konvertierungen, die auf dem Datenträger existieren, aber keinen Datenbankeintrag haben (z. B. nach DB-Verlust oder -Neustart). Erstellt fehlende Verlaufseinträge, damit sie in der Oberfläche erscheinen und neu geladen werden können.

Die Abgleichung erfolgt außerdem automatisch beim Anwendungsstart.

### Antwort

```json
{
  "message": "Reconciled 3 entries from disk",
  "added_count": 3,
  "added_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ]
}
```

### Hinweise

- Nur Ausgabeverzeichnisse mit gültigen UUID-Namen und mindestens einer Ausgabedatei (`.md`, `.html`, `.json` oder `.document.json`) werden abgeglichen
- Bereits vorhandene Einträge werden übersprungen

---

## Verlaufseintrag löschen

```http
DELETE /api/history/{job_id}
```

### Response

```json
{
  "message": "Entry deleted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Get History Statistics

```http
GET /api/history/stats
```

### Response

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

## Search History

```http
GET /api/history/search
```

### Query Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `limit` | int | No | Maximum results (default: 20) |

### Response

```json
{
  "entries": [...],
  "query": "invoice",
  "count": 5
}
```

---

## Export History

```http
GET /api/history/export
```

**Response**: JSON file download with all history entries

---

## Clear All History

```http
DELETE /api/history
```

### Response

```json
{
  "message": "All history entries deleted",
  "count": 150
}
```

