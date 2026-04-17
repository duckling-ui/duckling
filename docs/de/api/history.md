# Verlauf-API

Endpunkte für den Zugriff auf den Konvertierungsverlauf.

## Konvertierungsverlauf abrufen

```http
GET /api/history
```

### Abfrageparameter

| Name | Typ | Standard | Beschreibung |
|------|-----|----------|--------------|
| `limit` | int | 50 | Maximale Anzahl zurückgegebener Einträge |
| `offset` | int | 0 | Anzahl der zu überspringenden Einträge |
| `status` | string | - | Nach Status filtern |

### Antwort

```json
{
  "entries": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document_abc123.pdf",
      "original_filename": "Mein Dokument.pdf",
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

## Aktuellen Verlauf abrufen

```http
GET /api/history/recent
```

### Abfrageparameter

| Name | Typ | Standard | Beschreibung |
|------|-----|----------|--------------|
| `limit` | int | 10 | Maximale Anzahl zurückgegebener Einträge |

---

## Verlaufseintrag abrufen

```http
GET /api/history/{job_id}
```

### Antwort

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document_abc123.pdf",
  "original_filename": "Mein Dokument.pdf",
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

Lädt ein zuvor konvertiertes Dokument aus dem Verlauf und liefert es als Konvertierungsergebnis. Dieser Endpunkt lädt das `DoclingDocument` aus der gespeicherten JSON-Datei und gibt es im gleichen Format wie ein frisches Konvertierungsergebnis zurück.

### Pfadparameter

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `job_id` | string | Ja | Auftragskennung (muss mit `[A-Za-z0-9_-]+` übereinstimmen) |

### Antwort

Gibt ein `ConversionResult`-Objekt im Format einer frischen Konvertierung zurück:

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
  "preview": "# Vorschau des Dokumentinhalts..."
}
```

### Fehlerantworten

**404 Not Found**: Verlaufseintrag existiert nicht
```json
{
  "error": "Verlaufseintrag {job_id} nicht gefunden"
}
```

**400 Bad Request**: Konvertierung nicht abgeschlossen
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Konvertierung nicht abgeschlossen"
}
```

### Hinweise

- Funktioniert nur für abgeschlossene Konvertierungen
- Ist die gespeicherte Dokument-JSON-Datei nicht verfügbar, versucht der Endpunkt, das Ergebnis aus den Ausgabedateien zu rekonstruieren
- Dokumente werden nach jeder erfolgreichen Konvertierung automatisch gespeichert
- Das Feld `document_json_path` in Verlaufseinträgen zeigt an, wo die Dokument-JSON gespeichert ist

---

## Verlauf mit dem Datenträger abgleichen

```http
POST /api/history/reconcile
```

Durchsucht das Ausgabeverzeichnis nach Konvertierungsausgaben, die auf dem Datenträger existieren, aber keinen Datenbankeintrag haben (z. B. nach Datenverlust oder Neustart). Legt fehlende Verlaufseinträge an, damit sie in der Oberfläche erscheinen und erneut geladen werden können.

Der Abgleich wird außerdem automatisch beim Start der Anwendung ausgeführt.

### Antwort

```json
{
  "message": "3 Einträge vom Datenträger abgeglichen",
  "added_count": 3,
  "added_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ]
}
```

### Hinweise

- Es werden nur Ausgabeverzeichnisse mit gültigen UUID-Namen und mindestens einer Ausgabedatei (`.md`, `.html`, `.json` oder `.document.json`) abgeglichen
- Bereits in der Datenbank vorhandene Einträge werden übersprungen

---

## Chunks generieren

```http
POST /api/history/{job_id}/generate-chunks
```

Generiert RAG-Chunks für ein abgeschlossenes Dokument bei Bedarf. Lädt das DoclingDocument vom Datenträger, wendet die aktuellen Chunking-Einstellungen an und liefert die generierten Chunks. Speichert die Chunks auf dem Datenträger zum Herunterladen.

### Antwort

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": [
    {
      "id": 1,
      "text": "Chunk-Inhalt...",
      "meta": { "page": 1, "headings": ["Abschnittstitel"] }
    }
  ],
  "count": 42
}
```

**404 Not Found**: Verlaufseintrag oder Dokument nicht gefunden

---

## Verlaufseintrag löschen

```http
DELETE /api/history/{job_id}
```

### Antwort

```json
{
  "message": "Eintrag gelöscht",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Verlaufsstatistiken abrufen

```http
GET /api/history/stats
```

### Antwort

Liefert Konvertierungsstatistiken, Speichernutzung und Warteschlangentiefe. Das Objekt `conversions` enthält bei Verfügbarkeit erweiterte Kennzahlen.

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

## Verlauf durchsuchen

```http
GET /api/history/search
```

### Abfrageparameter

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `q` | string | Ja | Suchanfrage |
| `limit` | int | Nein | Maximale Trefferanzahl (Standard: 20) |

### Antwort

```json
{
  "entries": [...],
  "query": "Rechnung",
  "count": 5
}
```

---

## Verlauf exportieren

```http
GET /api/history/export
```

**Antwort**: JSON-Dateidownload mit allen Verlaufseinträgen

---

## Gesamten Verlauf löschen

```http
DELETE /api/history
```

### Antwort

```json
{
  "message": "Alle Verlaufseinträge gelöscht",
  "count": 150
}
```
