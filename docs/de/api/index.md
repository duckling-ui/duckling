# API-Referenz

Vollständige API-Dokumentation für das Duckling-Backend.

## Basis-URL

```
http://localhost:5001/api
```

## Authentifizierung

Derzeit ist für die API keine Authentifizierung erforderlich. Für Produktionsumgebungen sollten Sie eine Authentifizierungs-Middleware ergänzen.

## Abschnitte

<div class="grid cards" markdown>

-   :material-file-document-multiple:{ .lg .middle } __Konvertierung__

    ---

    Dokumente hochladen und konvertieren

    [:octicons-arrow-right-24: Konvertierungs-API](conversion.md)

-   :material-cog:{ .lg .middle } __Einstellungen__

    ---

    Konfiguration abrufen und aktualisieren

    [:octicons-arrow-right-24: Einstellungen-API](settings.md)

-   :material-history:{ .lg .middle } __Verlauf__

    ---

    Konvertierungsverlauf abrufen

    [:octicons-arrow-right-24: Verlaufs-API](history.md)

</div>

## Kurzreferenz

### Konvertierungs-Endpunkte

| Endpunkt | Methode | Beschreibung |
|----------|--------|-------------|
| `/convert` | POST | Einzelnes Dokument hochladen und konvertieren |
| `/convert/batch` | POST | Mehrere Dokumente stapelweise konvertieren |
| `/convert/{job_id}/status` | GET | Konvertierungsstatus abrufen |
| `/convert/{job_id}/result` | GET | Konvertierungsergebnis abrufen |
| `/convert/{job_id}/images` | GET | Extrahierte Bilder auflisten |
| `/convert/{job_id}/images/{id}` | GET | Extrahiertes Bild herunterladen |
| `/convert/{job_id}/tables` | GET | Extrahierte Tabellen auflisten |
| `/convert/{job_id}/tables/{id}/csv` | GET | Tabelle als CSV herunterladen |
| `/convert/{job_id}/chunks` | GET | Dokumentsegmente abrufen |
| `/export/{job_id}/{format}` | GET | Konvertierte Datei herunterladen |

### Einstellungen-Endpunkte

| Endpunkt | Methode | Beschreibung |
|----------|--------|-------------|
| `/settings` | GET/PUT | Alle Einstellungen abrufen/aktualisieren |
| `/settings/reset` | POST | Auf Standardwerte zurücksetzen |
| `/settings/formats` | GET | Unterstützte Formate auflisten |
| `/settings/ocr` | GET/PUT | OCR-Einstellungen |
| `/settings/tables` | GET/PUT | Tabelleneinstellungen |
| `/settings/images` | GET/PUT | Bildeinstellungen |
| `/settings/performance` | GET/PUT | Leistungseinstellungen |
| `/settings/chunking` | GET/PUT | Segmentierungseinstellungen |

### Verlaufs-Endpunkte

| Endpunkt | Methode | Beschreibung |
|----------|--------|-------------|
| `/history` | GET | Konvertierungsverlauf auflisten |
| `/history/{job_id}` | GET | Verlaufseintrag abrufen |
| `/history/stats` | GET | Konvertierungsstatistiken abrufen |
| `/history/search` | GET | Verlauf durchsuchen |

## Health Check

```http
GET /health
```

**Antwort**

```json
{
  "status": "healthy",
  "service": "duckling-backend"
}
```

## Fehlerantworten

Alle Endpunkte können Fehlerantworten im folgenden Format zurückgeben:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### HTTP-Statuscodes

| Code | Beschreibung |
|------|-------------|
| 200 | Erfolg |
| 202 | Akzeptiert (asynchrone Operation gestartet) |
| 400 | Fehlerhafte Anfrage (ungültige Eingabe) |
| 404 | Nicht gefunden |
| 413 | Nutzlast zu groß |
| 500 | Interner Serverfehler |

## Ratenbegrenzung

Derzeit ist keine Ratenbegrenzung implementiert. Für Produktionsumgebungen sollten Sie eine entsprechende Middleware ergänzen.

## CORS

Die API erlaubt domänenübergreifende Anfragen von der konfigurierten Frontend-Origin (Standard: `http://localhost:3000`).
