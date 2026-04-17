# Einstellungen-API

Endpunkte zur Verwaltung der Konvertierungseinstellungen.

!!! note "Sitzungsbasierte Speicherung"
    Einstellungen werden pro Benutzersitzung in der Datenbank gespeichert. Die Einstellungen jedes Benutzers sind isoliert und beeinträchtigen andere Benutzer nicht — Duckling ist damit für Mehrbenutzer-Betrieb geeignet.

## Alle Einstellungen abrufen

```http
GET /api/settings
```

### Antwort

```json
{
  "ocr": {
    "enabled": true,
    "language": "en",
    "force_full_page_ocr": false,
    "backend": "easyocr",
    "use_gpu": false,
    "confidence_threshold": 0.5,
    "bitmap_area_threshold": 0.05
  },
  "tables": {
    "enabled": true,
    "structure_extraction": true,
    "mode": "accurate",
    "do_cell_matching": true
  },
  "images": {
    "extract": true,
    "classify": true,
    "generate_page_images": false,
    "generate_picture_images": true,
    "generate_table_images": true,
    "images_scale": 1.0
  },
  "enrichment": {
    "code_enrichment": false,
    "formula_enrichment": false,
    "picture_classification": false,
    "picture_description": false
  },
  "output": {
    "default_format": "markdown"
  },
  "performance": {
    "device": "auto",
    "num_threads": 4,
    "document_timeout": null
  },
  "chunking": {
    "enabled": false,
    "max_tokens": 512,
    "merge_peers": true
  }
}
```

---

## Einstellungen aktualisieren

```http
PUT /api/settings
Content-Type: application/json
```

### Anfragetext

```json
{
  "ocr": {
    "language": "de",
    "backend": "tesseract"
  },
  "tables": {
    "mode": "fast"
  }
}
```

### Antwort

Gibt das aktualisierte Einstellungsobjekt zurück.

---

## Einstellungen auf Standard zurücksetzen

```http
POST /api/settings/reset
```

### Antwort

Gibt das Einstellungsobjekt mit Standardwerten zurück.

---

## Unterstützte Formate abrufen

```http
GET /api/settings/formats
```

### Antwort

```json
{
  "input_formats": [
    {"id": "pdf", "name": "PDF Document", "extensions": [".pdf"], "icon": "document"},
    {"id": "docx", "name": "Microsoft Word", "extensions": [".docx"], "icon": "document"},
    {"id": "image", "name": "Image", "extensions": [".png", ".jpg", ".jpeg", ".tiff"], "icon": "image"}
  ],
  "output_formats": [
    {"id": "markdown", "name": "Markdown", "extension": ".md", "mime_type": "text/markdown"},
    {"id": "html", "name": "HTML", "extension": ".html", "mime_type": "text/html"},
    {"id": "json", "name": "JSON", "extension": ".json", "mime_type": "application/json"}
  ]
}
```

---

## OCR-Einstellungen

### OCR-Einstellungen abrufen

```http
GET /api/settings/ocr
```

### OCR-Einstellungen aktualisieren

```http
PUT /api/settings/ocr
Content-Type: application/json
```

**Abfrageparameter:**

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `auto_install` | boolean | Bei `true` werden per pip installierbare Backends automatisch installiert |

### Antwort/Anfrage

```json
{
  "ocr": {
    "enabled": true,
    "language": "en",
    "force_full_page_ocr": false,
    "backend": "easyocr",
    "use_gpu": false,
    "confidence_threshold": 0.5,
    "bitmap_area_threshold": 0.05
  },
  "available_languages": [
    {"code": "en", "name": "English"},
    {"code": "de", "name": "German"},
    {"code": "fr", "name": "French"}
  ],
  "available_backends": [
    {"id": "easyocr", "name": "EasyOCR", "description": "Allgemeines OCR mit GPU-Unterstützung"},
    {"id": "tesseract", "name": "Tesseract", "description": "Klassische OCR-Engine"},
    {"id": "ocrmac", "name": "macOS Vision", "description": "Natives macOS-OCR (nur Mac)"},
    {"id": "rapidocr", "name": "RapidOCR", "description": "Schnelles OCR mit ONNX-Runtime"}
  ]
}
```

---

## OCR-Backend-Verwaltung

### Installationsstatus aller Backends abrufen

```http
GET /api/settings/ocr/backends
```

Liefert den Installationsstatus aller OCR-Backends.

### Antwort

```json
{
  "backends": [
    {
      "id": "easyocr",
      "name": "EasyOCR",
      "description": "General-purpose OCR with GPU support",
      "installed": true,
      "available": true,
      "error": null,
      "pip_installable": true,
      "requires_system_install": false,
      "platform": null,
      "note": "First run will download language models (~100MB per language)"
    },
    {
      "id": "tesseract",
      "name": "Tesseract",
      "description": "Classic OCR engine",
      "installed": false,
      "available": false,
      "error": "Package not installed",
      "pip_installable": true,
      "requires_system_install": true,
      "platform": null,
      "note": "Requires Tesseract to be installed on your system"
    }
  ],
  "current_platform": "darwin"
}
```

### Bestimmtes Backend prüfen

```http
GET /api/settings/ocr/backends/{backend_id}/check
```

### Antwort

```json
{
  "backend": "easyocr",
  "installed": true,
  "available": true,
  "error": null,
  "pip_installable": true,
  "requires_system_install": false,
  "note": "First run will download language models"
}
```

### Backend installieren

```http
POST /api/settings/ocr/backends/{backend_id}/install
```

Installiert ein per pip installierbares OCR-Backend.

### Antwort (Erfolg)

```json
{
  "message": "Successfully installed easyocr",
  "success": true,
  "installed": true,
  "available": true,
  "note": "First run will download language models"
}
```

### Antwort (bereits installiert)

```json
{
  "message": "easyocr is already installed and available",
  "already_installed": true
}
```

### Antwort (Systeminstallation erforderlich)

```json
{
  "message": "Failed to install tesseract",
  "success": false,
  "error": "tesseract requires system-level installation",
  "requires_system_install": true
}
```

---

## Tabelleneinstellungen

### Tabelleneinstellungen abrufen

```http
GET /api/settings/tables
```

### Tabelleneinstellungen aktualisieren

```http
PUT /api/settings/tables
Content-Type: application/json
```

### Anfrage/Antwort

```json
{
  "tables": {
    "enabled": true,
    "structure_extraction": true,
    "mode": "accurate",
    "do_cell_matching": true
  }
}
```

---

## Bildeinstellungen

### Bildeinstellungen abrufen

```http
GET /api/settings/images
```

### Bildeinstellungen aktualisieren

```http
PUT /api/settings/images
Content-Type: application/json
```

### Anfrage/Antwort

```json
{
  "images": {
    "extract": true,
    "classify": true,
    "generate_page_images": false,
    "generate_picture_images": true,
    "generate_table_images": true,
    "images_scale": 1.0
  }
}
```

---

## Anreicherungs-Einstellungen

### Anreicherungs-Einstellungen abrufen

```http
GET /api/settings/enrichment
```

### Antwort

```json
{
  "enrichment": {
    "code_enrichment": false,
    "formula_enrichment": false,
    "picture_classification": false,
    "picture_description": false
  },
  "options": {
    "code_enrichment": {
      "description": "Codeblöcke mit Spracherkennung und Syntaxhervorhebung anreichern",
      "default": false,
      "note": "Kann die Verarbeitungszeit erhöhen"
    },
    "formula_enrichment": {
      "description": "LaTeX-Darstellungen mathematischer Formeln extrahieren",
      "default": false,
      "note": "Verbessert die Formeldarstellung in Exporten"
    },
    "picture_classification": {
      "description": "Bilder nach Typ klassifizieren (Abbildung, Diagramm, Foto usw.)",
      "default": false,
      "note": "Fügt extrahierten Bildern semantische Tags hinzu"
    },
    "picture_description": {
      "description": "Bildbeschreibungen mit KI-Vision-Modellen erzeugen",
      "default": false,
      "note": "Zusätzlicher Modell-Download, deutlich längere Verarbeitung"
    }
  }
}
```

### Anreicherungs-Einstellungen aktualisieren

```http
PUT /api/settings/enrichment
Content-Type: application/json
```

### Anfrage

```json
{
  "code_enrichment": true,
  "formula_enrichment": true
}
```

### Antwort

```json
{
  "message": "Enrichment settings updated",
  "enrichment": {
    "code_enrichment": true,
    "formula_enrichment": true,
    "picture_classification": false,
    "picture_description": false
  }
}
```

| Feld | Typ | Beschreibung |
|-------|------|-------------|
| `code_enrichment` | boolean | Codeblöcke mit Spracherkennung anreichern |
| `formula_enrichment` | boolean | LaTeX aus mathematischen Formeln extrahieren |
| `picture_classification` | boolean | Bilder semantisch klassifizieren |
| `picture_description` | boolean | KI-Bildunterschriften erzeugen |

!!! warning "Verarbeitungszeit"
    Die Aktivierung von `formula_enrichment` und besonders `picture_description` kann die Dokumentverarbeitung deutlich verlängern.

---

## Leistungseinstellungen

### Leistungseinstellungen abrufen

```http
GET /api/settings/performance
```

### Leistungseinstellungen aktualisieren

```http
PUT /api/settings/performance
Content-Type: application/json
```

### Anfrage/Antwort

```json
{
  "performance": {
    "device": "auto",
    "num_threads": 4,
    "document_timeout": null
  }
}
```

---

## Segmentierungseinstellungen (Chunking)

### Segmentierungseinstellungen abrufen

```http
GET /api/settings/chunking
```

### Segmentierungseinstellungen aktualisieren

```http
PUT /api/settings/chunking
Content-Type: application/json
```

### Anfrage/Antwort

```json
{
  "chunking": {
    "enabled": false,
    "max_tokens": 512,
    "merge_peers": true
  }
}
```

---

## Ausgabe-Einstellungen

### Ausgabe-Einstellungen abrufen

```http
GET /api/settings/output
```

### Ausgabe-Einstellungen aktualisieren

```http
PUT /api/settings/output
Content-Type: application/json
```

### Anfrage/Antwort

```json
{
  "output": {
    "default_format": "markdown"
  }
}
```
