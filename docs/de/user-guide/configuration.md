# Konfigurationshandbuch

Vollständige Referenz für alle Duckling-Konfigurationsoptionen.

## Umgebungsvariablen

Legen Sie eine `.env`-Datei im Verzeichnis `backend` an:

```env
# Flask Configuration
FLASK_ENV=development          # development | production | testing
SECRET_KEY=your-secret-key     # Required for production
DEBUG=True                     # Enable debug mode

# File Handling
MAX_CONTENT_LENGTH=104857600   # Max upload size in bytes (100MB default)

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///history.db
```

### Produktionsumgebung

```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key-here
DEBUG=False
MAX_CONTENT_LENGTH=209715200   # 200MB for production
```

!!! danger "Sicherheitshinweis"
    Verwenden Sie in der Produktion niemals den Standard-`SECRET_KEY`. Erzeugen Sie einen sicheren Zufallsschlüssel.

---

## OCR-Einstellungen

OCR (optische Zeichenerkennung) extrahiert Text aus Bildern und gescannten Dokumenten.

### Konfigurationsoptionen

| Einstellung | Typ | Standard | Beschreibung |
|-------------|-----|----------|--------------|
| `enabled` | boolean | `true` | OCR ein-/ausschalten |
| `backend` | string | `"easyocr"` | Zu verwendende OCR-Engine |
| `language` | string | `"en"` | Hauptsprache für die Erkennung |
| `force_full_page_ocr` | boolean | `false` | Ganze Seite per OCR vs. erkannte Bereiche |
| `use_gpu` | boolean | `false` | GPU-Beschleunigung (nur EasyOCR) |
| `confidence_threshold` | float | `0.5` | Mindest-Konfidenz der Ergebnisse (0–1) |
| `bitmap_area_threshold` | float | `0.05` | Mindestflächenanteil für Bitmap-OCR (0–1) |

### OCR-Engines

=== "EasyOCR"

    Gut für mehrsprachige Dokumente mit hohen Genauigkeitsanforderungen.

    ```json
    {
      "ocr": {
        "backend": "easyocr",
        "use_gpu": true,
        "language": "en"
      }
    }
    ```

    - **GPU-Unterstützung**: Ja (CUDA)
    - **Sprachen**: 80+
    - **Hinweis**: Auf manchen Systemen können Initialisierungsprobleme auftreten

=== "Tesseract"

    Klassische, zuverlässige OCR-Engine für einfache Dokumente.

    ```json
    {
      "ocr": {
        "backend": "tesseract",
        "language": "eng"
      }
    }
    ```

    - **GPU-Unterstützung**: Nein
    - **Sprachen**: 100+
    - **Voraussetzung**: Tesseract systemweit installiert

=== "macOS Vision"

    Native macOS-OCR mit Apples Vision-Framework.

    ```json
    {
      "ocr": {
        "backend": "ocrmac",
        "language": "en"
      }
    }
    ```

    - **GPU-Unterstützung**: Nutzt die Apple Neural Engine
    - **Voraussetzung**: macOS 10.15+
    - **Sprachcodes**: Duckling akzeptiert Kurzcodes wie `en`, `de`, `fr` und normalisiert sie bei der Konvertierung zu Vision-Lokalisierungen (z. B. `en-US`).

=== "RapidOCR"

    Schnelle, schlanke OCR mit ONNX Runtime.

    ```json
    {
      "ocr": {
        "backend": "rapidocr",
        "language": "en"
      }
    }
    ```

    - **GPU-Unterstützung**: Nein
    - **Sprachen**: begrenzt

### Unterstützte Sprachen

| Code | Sprache | Code | Sprache |
|------|---------|------|---------|
| `en` | Englisch | `ja` | Japanisch |
| `de` | Deutsch | `zh` | Chinesisch (vereinfacht) |
| `fr` | Französisch | `zh-tw` | Chinesisch (traditionell) |
| `es` | Spanisch | `ko` | Koreanisch |
| `it` | Italienisch | `ar` | Arabisch |
| `pt` | Portugiesisch | `hi` | Hindi |
| `nl` | Niederländisch | `th` | Thai |
| `pl` | Polnisch | `vi` | Vietnamesisch |
| `ru` | Russisch | `tr` | Türkisch |

---

## Tabelleneinstellungen

Legen Sie fest, wie Tabellen in Dokumenten erkannt und extrahiert werden.

### Konfigurationsoptionen

| Einstellung | Typ | Standard | Beschreibung |
|-------------|-----|----------|--------------|
| `enabled` | boolean | `true` | Tabellenerkennung aktivieren |
| `structure_extraction` | boolean | `true` | Tabellenstruktur beibehalten |
| `mode` | string | `"accurate"` | Erkennungsmodus |
| `do_cell_matching` | boolean | `true` | Zellinhalt der Struktur zuordnen |

### Erkennungsmodi

=== "Präziser Modus"

    ```json
    {
      "tables": {
        "enabled": true,
        "mode": "accurate",
        "do_cell_matching": true
      }
    }
    ```

    - Präzisere Tabellenerkennung
    - Bessere Zellgrenzen
    - Langsamere Verarbeitung
    - Empfohlen für komplexe Tabellen

=== "Schneller Modus"

    ```json
    {
      "tables": {
        "enabled": true,
        "mode": "fast",
        "do_cell_matching": false
      }
    }
    ```

    - Schnellere Verarbeitung
    - Gut für einfache Tabellen
    - Kann komplexe Strukturen übersehen

---

## Bildeinstellungen

Bildextraktion und -verarbeitung konfigurieren.

### Konfigurationsoptionen

| Einstellung | Typ | Standard | Beschreibung |
|-------------|-----|----------|--------------|
| `extract` | boolean | `true` | Eingebettete Bilder extrahieren |
| `classify` | boolean | `true` | Bilder klassifizieren und taggen |
| `generate_page_images` | boolean | `false` | Pro Seite ein Bild erzeugen |
| `generate_picture_images` | boolean | `true` | Abbildungen als Dateien extrahieren |
| `generate_table_images` | boolean | `true` | Tabellen als Bilder extrahieren |
| `images_scale` | float | `1.0` | Skalierungsfaktor für Bilder (0,1–4,0) |

### Beispielkonfigurationen

=== "Hohe Qualität"

    ```json
    {
      "images": {
        "extract": true,
        "classify": true,
        "generate_page_images": true,
        "generate_picture_images": true,
        "generate_table_images": true,
        "images_scale": 2.0
      }
    }
    ```

=== "Minimal (nur Text)"

    ```json
    {
      "images": {
        "extract": false,
        "classify": false,
        "generate_page_images": false,
        "generate_picture_images": false,
        "generate_table_images": false
      }
    }
    ```

---

## Leistungseinstellungen

Verarbeitungsgeschwindigkeit und Ressourcennutzung optimieren.

### Konfigurationsoptionen

| Einstellung | Typ | Standard | Beschreibung |
|-------------|-----|----------|--------------|
| `device` | string | `"auto"` | Verarbeitungsgerät |
| `num_threads` | int | `4` | CPU-Threads (1–32) |
| `document_timeout` | int/null | `null` | Maximale Bearbeitungszeit in Sekunden |

### Geräteoptionen

| Gerät | Beschreibung | Ideal für |
|-------|--------------|-----------|
| `auto` | Wählt automatisch das beste Gerät | Allgemeine Nutzung |
| `cpu` | Erzwingt CPU-Verarbeitung | Server ohne GPU |
| `cuda` | NVIDIA-GPU-Beschleunigung | Linux/Windows mit NVIDIA-GPU |
| `mps` | Apple Metal Performance Shaders | macOS mit Apple Silicon |

### Beispielkonfigurationen

=== "Hohe Leistung (GPU)"

    ```json
    {
      "performance": {
        "device": "cuda",
        "num_threads": 8,
        "document_timeout": null
      }
    }
    ```

=== "Begrenzte Ressourcen"

    ```json
    {
      "performance": {
        "device": "cpu",
        "num_threads": 2,
        "document_timeout": 60
      }
    }
    ```

=== "Apple Silicon"

    ```json
    {
      "performance": {
        "device": "mps",
        "num_threads": 4,
        "document_timeout": null
      }
    }
    ```

---

## Chunking-Einstellungen

Dokument-Chunking für RAG-Anwendungen konfigurieren.

### Konfigurationsoptionen

| Einstellung | Typ | Standard | Beschreibung |
|-------------|-----|----------|--------------|
| `enabled` | boolean | `false` | Chunking aktivieren |
| `max_tokens` | int | `512` | Maximale Token pro Segment |
| `merge_peers` | boolean | `true` | Zu kleine Segmente zusammenführen |

### Beispielkonfigurationen

=== "Für RAG optimiert"

    ```json
    {
      "chunking": {
        "enabled": true,
        "max_tokens": 512,
        "merge_peers": true
      }
    }
    ```

=== "Große Kontextfenster"

    ```json
    {
      "chunking": {
        "enabled": true,
        "max_tokens": 2048,
        "merge_peers": false
      }
    }
    ```

---

## Ausgabe-Einstellungen

Standard-Ausgabeformat festlegen.

| Einstellung | Typ | Standard | Beschreibung |
|-------------|-----|----------|--------------|
| `default_format` | string | `"markdown"` | Standard-Exportformat |

---

## Vollständiges Konfigurationsbeispiel

```json
{
  "ocr": {
    "enabled": true,
    "backend": "easyocr",
    "language": "en",
    "force_full_page_ocr": false,
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
  "performance": {
    "device": "auto",
    "num_threads": 4,
    "document_timeout": null
  },
  "chunking": {
    "enabled": false,
    "max_tokens": 512,
    "merge_peers": true
  },
  "output": {
    "default_format": "markdown"
  }
}
```

---

## Konfiguration über die API

### Aktuelle Einstellungen abrufen

```bash
curl http://localhost:5001/api/settings
```

### Einstellungen aktualisieren

```bash
curl -X PUT http://localhost:5001/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "ocr": {"backend": "tesseract"},
    "performance": {"num_threads": 8}
  }'
```

### Auf Standardwerte zurücksetzen

```bash
curl -X POST http://localhost:5001/api/settings/reset
```

---

## Fehlerbehebung

### OCR funktioniert nicht

1. **EasyOCR-Initialisierungsfehler**: Wechseln Sie zu `ocrmac` (macOS) oder `tesseract`
2. **GPU-Fehler**: Setzen Sie `use_gpu: false`
3. **Niedrige Konfidenz**: Senken Sie `confidence_threshold`

### Langsame Verarbeitung

1. `images_scale` auf `0.5` reduzieren
2. Für Tabellen `mode: "fast"` verwenden
3. `generate_page_images` deaktivieren
4. `num_threads` erhöhen

### Speicherprobleme

1. `document_timeout` aktivieren (z. B. 120 Sekunden)
2. Weniger Dateien pro Stapel verarbeiten
3. `images_scale` reduzieren
4. Chunking deaktivieren, falls nicht benötigt
