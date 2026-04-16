# Konvertierungs-API

Endpunkte zum Hochladen und Konvertieren von Dokumenten.

## Einzelnes Dokument hochladen und konvertieren

```http
POST /api/convert
Content-Type: multipart/form-data
```

### Parameter

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `file` | Datei | Ja | Zu konvertierendes Dokument |
| `settings` | JSON-Zeichenkette | Nein | Überschreibende Konvertierungseinstellungen |

### Beispielanfrage

```bash
curl -X POST http://localhost:5001/api/convert \
  -F "file=@document.pdf" \
  -F 'settings={"ocr":{"enabled":true,"language":"en"}}'
```

### Antwort (202 Accepted)

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

## Mehrere Dokumente stapelweise konvertieren

```http
POST /api/convert/batch
Content-Type: multipart/form-data
```

### Parameter

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `files` | Datei[] | Ja | Zu konvertierende Dokumente (das Feld `files` für jeden Multipart-Teil wiederholen). Ordner-Uploads aus der Oberfläche haben dieselbe Form: ein Multipart-Teil pro Datei, nachdem der Browser das Verzeichnis aufgelöst hat. |
| `settings` | JSON-Zeichenkette | Nein | Überschreibende Konvertierungseinstellungen |

**Unterstützte Typen:** Jeder Dateiname muss eine vom Server erlaubte Endung haben (siehe Deployment `ALLOWED_EXTENSIONS`). Nicht unterstützte Teile werden nicht konvertiert; sie erscheinen in der Antwort mit `"status": "rejected"`. Wenn **jeder** Teil nicht unterstützt ist (oder sonst keine Konvertierung erzeugt), antwortet die API mit **400**, einer `error`-Meldung und der pro-Datei-Liste `jobs`.

**Anfragegröße:** Der gesamte Multipart-Body muss unter `MAX_CONTENT_LENGTH` liegen (Standard 100 MB für die ganze Anfrage), nicht pro Datei. Große Ordner ggf. in mehrere Batch-Anfragen aufteilen.

### Beispielanfrage

```bash
curl -X POST http://localhost:5001/api/convert/batch \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "files=@image.png"
```

### Antwort (202 Accepted)

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

### Antwort (400 Bad Request)

Wird zurückgegeben, wenn keine Konvertierungsjobs gestartet werden (z. B. hat jede Datei eine unzulässige Endung):

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

## Dokument von URL konvertieren

```http
POST /api/convert/url
Content-Type: application/json
```

### Parameter

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `url` | string | Ja | URL des zu konvertierenden Dokuments |
| `settings` | object | Nein | Überschreibende Konvertierungseinstellungen |

### Beispielanfrage

```bash
curl -X POST http://localhost:5001/api/convert/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/document.pdf",
    "settings": {"ocr": {"enabled": true}}
  }'
```

### Antwort (202 Accepted)

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

## Dokumente von URLs stapelweise konvertieren

```http
POST /api/convert/url/batch
Content-Type: application/json
```

### Parameter

| Name | Typ | Erforderlich | Beschreibung |
|------|-----|--------------|--------------|
| `urls` | string[] | Ja | Array von URLs zur Konvertierung |
| `settings` | object | Nein | Überschreibende Konvertierungseinstellungen |

### Beispielanfrage

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

### Antwort (202 Accepted)

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

## Konvertierungsstatus abrufen

```http
GET /api/convert/{job_id}/status
```

### Antwort (in Bearbeitung)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "message": "Analyzing document with OCR (easyocr, en)..."
}
```

### Antwort (abgeschlossen)

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
  "preview": "# Document Title\n\nFirst paragraph..."
}
```

### Antwort (fehlgeschlagen)

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

## Konvertierungsergebnis abrufen

```http
GET /api/convert/{job_id}/result
```

### Antwort

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "confidence": 0.92,
  "formats_available": ["markdown", "html", "json", "text", "doctags", "document_tokens"],
  "result": {
    "markdown_preview": "# Document Title\n\nContent preview...",
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

## Extrahierte Bilder abrufen

```http
GET /api/convert/{job_id}/images
```

### Antwort

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "images": [
    {
      "id": 1,
      "filename": "image_1.png",
      "path": "/outputs/job_id/images/image_1.png",
      "caption": "Figure 1: Architecture diagram",
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

## Extrahiertes Bild herunterladen

```http
GET /api/convert/{job_id}/images/{image_id}
```

**Antwort:** Binäre Bilddatei (PNG)

---

## Extrahierte Tabellen abrufen

```http
GET /api/convert/{job_id}/tables
```

### Antwort

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "tables": [
    {
      "id": 1,
      "label": "table",
      "caption": "Table 1: Sales Data",
      "rows": [
        ["Product", "Q1", "Q2", "Q3", "Q4"],
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

## Tabelle als CSV herunterladen

```http
GET /api/convert/{job_id}/tables/{table_id}/csv
```

**Antwort:** CSV-Datei

---

## Tabelle als Bild herunterladen

```http
GET /api/convert/{job_id}/tables/{table_id}/image
```

**Antwort:** Binäre Bilddatei (PNG)

---

## Dokumentsegmente (Chunks) abrufen

```http
GET /api/convert/{job_id}/chunks
```

### Antwort

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": [
    {
      "id": 1,
      "text": "Erster Textabschnitt aus dem Dokument …",
      "meta": {
        "headings": ["Introduction"],
        "page": 1
      }
    },
    {
      "id": 2,
      "text": "Zweiter Abschnitt setzt den Inhalt fort …",
      "meta": {
        "headings": ["Introduction", "Background"],
        "page": 1
      }
    }
  ],
  "count": 2
}
```

---

## Dokument exportieren

```http
GET /api/export/{job_id}/{format}
```

### Unterstützte Formate

- `markdown`
- `html`
- `json`
- `text`
- `doctags`
- `document_tokens`
- `chunks`

**Antwort:** Dateidownload mit passendem MIME-Typ

---

## Auftrag löschen

```http
DELETE /api/convert/{job_id}
```

### Antwort

```json
{
  "message": "Job 550e8400-e29b-41d4-a716-446655440000 deleted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```
