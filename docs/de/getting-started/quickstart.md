# Schnellstart

Starten Sie in 5 Minuten mit Duckling.

## Anwendung starten

Wählen Sie Ihre bevorzugte Methodee:

=== "Docker (empfohlen)"

    Der schnellste Weg zum Start - keine Abhängigkeiten zu installieren!

    **Option 1: Vorgefertigte Images (am schnellsten)**
    ```bash
    # Download the compose file
    curl -O https://raw.githubusercontent.com/davidgs/duckling/main/docker-compose.prebuilt.yml

    # Start Duckling
    docker-compose -f docker-compose.prebuilt.yml up -d
    ```

    **Option 2: Lokal erstellen**
    ```bash
    # Clone and start
    git clone https://github.com/davidgs/duckling.git
    cd duckling
    docker-compose up --build
    ```

    Die Benutzeroberfläche ist verfügbar unter `http://localhost:3000`

    !!! tip "Erster Start"
        Der erste Start kann einige Minuten dauern, da Docker die Images herunterlädt/erstellt.

=== "Manuelle Einrichtung"

    ### Terminal 1: Backend

    ```bash
    cd backend
    source venv/bin/activate  # Windows: venv\Scripts\activate
    python duckling.py
    ```

    Die API ist verfügbar unter `http://localhost:5001`

    ### Terminal 2: Frontend

    ```bash
    cd frontend
    npm run dev
    ```

    Die Benutzeroberfläche ist verfügbar unter `http://localhost:3000`

## Ihre erste Konvertierung

### 1. Anwendung öffnen

Navigieren Sie zu `http://localhost:3000` in Ihrem Browser.

<figure markdown="span">
  ![Duckling Interface](../assets/screenshots/ui/main-english.png){ loading=lazy }
  <figcaption>Die Hauptoberfläche von Duckling</figcaption>
</figure>

### 2. Dokument hochladen

Ziehen Sie eine PDF-, Word-Datei oder ein Bild in die Ablagezone oder klicken Sie zum Durchsuchen.

<figure markdown="span">
  ![Uploading Document](../assets/screenshots/ui/dropzone-uploading.svg){ loading=lazy }
  <figcaption>Fortschrittsanzeige beim Hochladen</figcaption>
</figure>

### 3. Fortschritt beobachten

Der Konvertierungsfortschritt wird in Echtzeit angezeigt.

<figure markdown="span">
  ![Konvertierung Progress](../assets/screenshots/features/conversion-progress.svg){ loading=lazy }
  <figcaption>Echtzeit-Konvertierungsfortschritt</figcaption>
</figure>

### 4. Ergebnisse herunterladen

Wählen Sie nach Abschluss Ihr Exportformat:

<figure markdown="span">
  ![Konvertierung Complete](../assets/screenshots/features/conversion-complete.svg){ loading=lazy }
  <figcaption>Konvertierung abgeschlossen mit Exportoptionen</figcaption>
</figure>

- **Markdown** - Ideal für Dokumentation
- **HTML** - Webfertige Ausgabe
- **JSON** - Vollständige Dokumentstruktur
- **Klartext** - Einfache Textextraktion

## Grundkonfiguration

Klicken Sie auf :material-cog: **Einstellungen** Schaltfläche zum Konfigurieren:

### OCR-Einstellungen

| Einstellung | Stundard | Beschreibung |
|---------|---------|-------------|
| Aktiviert | `true` | OCR für gescannte Dokumente aktivieren |
| Backend | `easyocr` | Zu verwendende OCR-Engine |
| Sprache | `en` | Hauptsprache |

### Tabelleneinstellungen

| Einstellung | Stundard | Beschreibung |
|---------|---------|-------------|
| Aktiviert | `true` | Tabellen aus Dokumenten extrahieren |
| Modus | `genau` | Erkennungsgenauigkeitsstufe |

### Bildeinstellungen

| Einstellung | Stundard | Beschreibung |
|---------|---------|-------------|
| Extrahieren | `true` | Eingebettete Bilder extrahieren |
| Skalierung | `1.0` | Bildausgabeskalierung |

## Stapelverarbeitung

Um mehrere Dateien gleichzeitig zu konvertieren:

1. Aktivieren **Stapelmodus** in der Kopfzeile
2. Ziehen Sie mehrere Dateien in die Ablagezone
3. Alle Dateien werden gleichzeitig verarbeitet

<figure markdown="span">
  ![Stapelmodus](../assets/screenshots/ui/dropzone-batch.png){ loading=lazy }
  <figcaption>Stapelmodus mit mehreren Dateien</figcaption>
</figure>

!!! tip "Leistung"
    Die Stapelverarbeitung verwendet eine Job-Warteschlange mit maximal 2 gleichzeitigen Konvertierungen, um Speichererschöpfung zu vermeiden.

## API verwenden

Für programmatischen Zugriff verwenden Sie die REST-API:

```bash
# Upload and convert a document
curl -X POST http://localhost:5001/api/convert \
  -F "file=@document.pdf"

# Response
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

Siehe die [API-Referenz](../api/index.md) für vollständige Dokumentation.

## Nächste Schritte

- [Funktionen](../user-guide/features.md) - Alle Funktionen erkunden
- [Konfiguration](../user-guide/configuration.md) - Erweiterte Einstellungen
- [API-Referenz](../api/index.md) - In Ihre Apps integrieren

