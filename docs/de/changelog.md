# Changelog

Alle bemerkenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
und dieses Projekt folgt der [Semantischen Versionierung](https://semver.org/spec/v2.0.0.html).

**Neueste Version:** [0.0.11](https://github.com/davidgs/duckling/releases/tag/v0.0.11) (2026-03-30)

## [Unveröffentlicht]

### Geplant

- Benutzerauthentifizierung
- Cloud-Speicher-Integration
- Konvertierungsvorlagen
- API-Ratenbegrenzung
- WebSocket für Echtzeit-Updates
- Dunkel-/Hell-Theme-Umschalter
- Tastaturkürzel
- Barrierefreiheitsverbesserungen (WCAG 2.1)

## [0.0.11] - 2026-03-30

### Geändert

- **Upload-UX**: Vereinheitlichte Ablagezone ohne separaten Stapel-Schalter in der Kopfzeile; siehe `CHANGELOG.md` im Repository-Root.

### Behoben

- **Frontend-Tests**: Der Iframe-Navigationstest für `DocsPanel` wartet nach abgeschlossenem gemocktem `fetch` auf die Registrierung des `message`-Listeners und nutzt ein längeres `waitFor`-Timeout, damit die CI auf langsameren Runnern stabil bleibt.

## [0.0.10a] - 2026-03-23

### Behoben

- **Backend-Abhängigkeiten**: Eine einzige Datei `backend/requirements.txt` für API und In-App-MkDocs-Builds; doppelte `backend/requirements-docs.txt` entfernt.

### Geändert

- **Dokumentationsnavigation**: Wechsel von horizontalen Top-Tabs zu einer einzelnen linken Seitenleiste mit aufklappbarer Baumnavigation; jede Hauptkategorie (Startseite, Erste Schritte usw.) kann ein- oder ausgeklappt werden.
- **Schlüsselfunktionen-Kacheln**: Jede Funktionskachel auf der Dokumentations-Startseite ist jetzt ein klickbarer Link zu ihrer detaillierten Dokumentation (Seite Funktionen oder Formate).
- **CONTRIBUTING.md**: DCO-Signatur (Developer Certificate of Origin) für alle Commits hinzugefügt.
- **Contributing-Dokumentation**: Vollständige Übersetzungen für Deutsch (de), Spanisch (es) und Französisch (fr); alle Locales haben jetzt konsistenten, vollständigen Inhalt inklusive DCO-Anforderungen.

### Sicherheit

- Rollup Path-Traversal (GHSA-mw96-cpmx-2vgc) und Minimatch ReDoS (GHSA-3ppc-4f35-3m26) per npm-Overrides im Frontend behoben: `rollup >=4.59.0`, `minimatch 9.0.6` für `@typescript-eslint/typescript-estree`.
- Werkzeug safe_join für Windows-Gerätenamen in mehrsegmentigen Pfaden behoben (CVE-2026-27199, GHSA-29vq-49wr-vm6x): werkzeug 3.1.4 → 3.1.6.
- Flask-Session Vary: Cookie-Header bei Verwendung des `in`-Operators behoben (CVE-2026-27205): flask 3.0.0 → 3.1.3.
- **SSRF-Prävention**: URL-Validierung vor ausgehenden Anfragen in `download_from_url`, `download_from_url_with_images` und `download_image`; blockiert Loopback, private IPs, Link-Local, Metadata und gefährliche Schemas.
- **CodeQL-Sicherheitsfixes**:
  - SSRF: `validate_url_safe_for_request` gibt jetzt die validierte URL zurück; alle `requests.get`-Aufrufe verwenden den Rückgabewert zur Erfüllung der Datenflussanalyse.
  - ReDoS: HTML-Bildextraktion vor Regex-Verarbeitung auf 5 MB begrenzt, um polynomielle Regex auf benutzerkontrolliertem Inhalt zu mindern.
  - Path-Traversal: `delete_output_folder` verwendet jetzt `validate_job_id` und `get_validated_output_dir` aus den Sicherheits-Utilities statt manueller Prüfungen.
  - Informationsoffenlegung: Einstellungs-API-Fehlerantworten werden über `_sanitize_error_for_client` bereinigt, um Stack-Trace- oder sensible Datenlecks zu verhindern.

## [0.0.10a] - 2026-02-24

### Hinzugefügt

- **Docker-Image-Publishing-Workflow**: GitHub Action läuft bei PR-Merges in `main`, baut Multi-Platform-Images und pusht zu Docker Hub und GitHub Container Registry (benötigt `DOCKERHUB_USERNAME`- und `DOCKERHUB_TOKEN`-Secrets).
- **Chunks jetzt generieren**: Button im RAG-Chunks-Tab zur bedarfsgesteuerten Chunk-Generierung für abgeschlossene Dokumente (`POST /api/history/{job_id}/generate-chunks`)
- **Inhaltsadressierte Deduplizierung**: Gleiche Datei + gleiche dokumentbeeinflussende Einstellungen nutzen gespeicherten Inhalt statt Neu-Konvertierung
  - Cache-Treffer: Symlink erstellen, Metadaten laden, sofort abschließen (kein Docling-Lauf)
  - Cache-Fehler: Konvertierung ausführen, Ausgabe in Content-Store verschieben, Symlink erstellen
  - Datenbank-Migration `scripts/migrate_add_content_hash.py` fügt Spalte `content_hash` hinzu
- **Konvertierungsstatistiken und -metriken**: Erweiterte History-Statistiken für Docling- und Duckling-Nutzungsanalysen
  - `GET /api/history/stats` liefert `avg_processing_seconds`, `ocr_backend_breakdown`, `output_format_breakdown`, `performance_device_breakdown`, `chunking_enabled_count`, `error_category_breakdown`, `source_type_breakdown` und `queue_depth`
  - Datenbank-Migration `scripts/migrate_add_stats_columns.py` fügt Stats-Spalten zur conversions-Tabelle hinzu
  - History-Panel zeigt durchschnittliche Verarbeitungszeit und Warteschlangentiefe, wenn verfügbar
- **Statistik-Panel**: Dedizierter Viewer für Konvertierungsstatistiken (Header-Button, „Vollständige Statistiken anzeigen“ aus History)
- **Erweiterte Statistiken**: Hardware- und Leistungsmetriken im Statistik-Panel
  - System-Abschnitt: Hardware-Typ (CPU/CUDA/MPS), CPU-Anzahl, aktuelle CPU-Auslastung, GPU-Infos
  - Durchschnittliche Seiten/Sek und Seiten/Sek pro CPU
  - Konvertierungszeitverteilung (Median, 95., 99. Perzentil)
  - Seiten/Sek-Diagramm über Zeit
  - CPU-Auslastung während jeder Konvertierung gemittelt (in DB gespeichert)
  - Datenbank-Migration `scripts/migrate_add_cpu_usage_column.py` fügt Spalte `cpu_usage_avg_during_conversion` hinzu
  - CPU-Auslastung ist jetzt prozessspezifisch (Duckling-Backend-Prozess, führt Docling aus), nicht systemweit
  - Pro-Konvertierung-Konfiguration gespeichert: `performance_device_used` (von „auto“ bei Abschluss aufgelöst), `images_classify_enabled`
  - Datenbank-Migration `scripts/migrate_add_config_columns.py` fügt diese Spalten hinzu
  - Stats-Aufschlüsselung nach Hardware, OCR-Backend, Bildklassifikator (Seiten/Sek, Konvertierungszeit pro Konfiguration)
- UI-Sprachunterstützung (Englisch `en`, Spanisch `es`, Französisch `fr`, Deutsch `de`) mit Sprachumschalter.
- Mehrsprachige MkDocs-Dokumentation (Englisch, Spanisch, Französisch, Deutsch) unter `/api/docs/site/<locale>/`.
- Dropzone-Panel-Kategoriebeschriftungen (Dokumente, Web, Bilder, Daten) jetzt vollständig internationalisiert.
- Docling-Docs-Abschnitt in MkDocs (kuratierte, vendored Teilmenge der Upstream-Docling-Dokumentation + Sync-Skript).
- **Sitzungsbasierte Benutzereinstellungen**: Benutzereinstellungen pro Sitzung in der Datenbank statt in einer gemeinsamen Datei gespeichert.

### Sicherheit

- Frontend-Sicherheitslücken behoben (esbuild GHSA-67mh-4wv8-2f99): Vite 5→7, Vitest 1→4 und zugehörige Abhängigkeiten aktualisiert.

### Geändert

- Backend-Einstiegspunkt von `app.py` zu `duckling.py` umbenannt für bessere Klarheit.
- Flask-Anwendungsname zu „duckling“ geändert (zeigt „Serving Flask app 'duckling'“).

### Behoben

- Die Dokumentationsnavigation zeigt jetzt vollständig lokalisierte Seitennamen in allen unterstützten Sprachen an.
- Kategoriebeschriftungen für Dateiformate im Dropzone-Panel werden jetzt korrekt basierend auf der ausgewählten Sprache übersetzt.
- Verbesserte Extraktion von Dokumentationsseitentiteln mit besserem Fallback auf übersetzte Namen.
- Prev/Next-Links in der Fußzeile des eingebetteten Docs-Panels bleiben innerhalb der aktuellen Seitenleisten-Kategorie, und die Navigation innerhalb der eingebetteten Docs hält die Seitenleisten-Auswahl synchron.
- Fehlgeschlagener Docs-Rebuild der eingebetteten App mit `cannot access local variable 'shutil'` beim MkDocs-Site-Build behoben.
- Backend-Docs-Rebuild bevorzugt jetzt die repo-lokale `./venv` MkDocs-Umgebung, um erforderliche Plugins (wie `i18n`) sicherzustellen.
- Behoben: Klick auf History-Eintrag lud Dokument nicht; verwendet jetzt den History-Load-Endpoint (Festplatte) statt des In-Memory-Ergebnis-Endpoints.
- Wenn `document_json_path` in der DB fehlt, findet und lädt History-Load jetzt `*.document.json` aus dem Ausgabeverzeichnis, sodass alle History-Einträge geladen werden, nicht nur der erste.
- Dokumentenansichts-Panel aktualisiert sich jetzt beim Laden eines anderen History-Eintrags (verwendet Komponenten-Key zum Remount mit frischem Zustand).
- `vitest.config.ts` für Vitest-4-Kompatibilität aktualisiert.
- CI/CD Node.js-Versionsanforderung auf 22 aktualisiert (erforderlich für Vite 7).

## [0.0.9] - 2026-01-08

### Hinzugefügt

- **Custom Branding**: Duckling-Logo und Versionsanzeige in der Kopfzeile.
- **URL-basierte Dokumentenkonvertierung**: Konvertierung von URLs mit automatischer Bildextraktion für HTML.
- **Dokumentenanreicherungsoptionen**: Code-, Formel-, Bildklassifizierung und Bildbeschreibung.
- **Enrichment-Modell-Vorab-Download**: KI-Modelle vor der Verarbeitung herunterladen.
- **Bildvorschau-Galerie**: Visuelle Miniaturansichten mit Lightbox-Viewer.
- **OCR-Backend-Auto-Installation**: Ein-Klick-Installation für pip-installierbare Backends.
- **Format-spezifische Vorschau**: Vorschau-Panel zeigt Inhalt im gewählten Exportformat.
- **Gerendert vs. Roh-Vorschau-Modus**: Umschalter für HTML und Markdown.
- **Erweiterte Docker-Unterstützung**: Multi-Stage-Dockerfiles, docker-compose-Varianten, Multi-Platform-Builds.

### Behoben

- Multi-Worker-Inhaltsabruf (Bilder, Tabellen, Ergebnisse).
- HTML-Vorschau in der UI.
- URL-Bildextraktion für nicht in Anführungszeichen gesetzte `src`-Attribute.
- Dokumentations-Panel bedient jetzt vorgefertigte MkDocs-Site.
- Umgebungsvariablen und `.env`-Laden.
- Groß-/kleinschreibungsunabhängige Dateiendungen.
- Konfidenz-Score und OCR-Backend-Auswahl.

## [0.0.8] - 2026-01-07

### Geändert

- **Umbenannt**: Projekt von „Docling UI“ zu „Duckling“ umbenannt
  - Alle Dokumentation, Code und Konfigurationsdateien aktualisiert
  - Branding in der gesamten Anwendung aktualisiert

## [0.0.7] - 2026-01-07

### Hinzugefügt

- **MkDocs-Dokumentation**: Dokumentation zu MkDocs mit Material-Theme migriert
  - Moderne, durchsuchbare Dokumentationsseite
  - Dunkel-/Hell-Theme-Umschalter
  - Mermaid-Diagramm-Unterstützung
  - Verbesserte Navigation und Organisation

### Geändert

- Dokumentationsstruktur für bessere Navigation reorganisiert
- Alle Diagramme in Mermaid-Format für Live-Rendering konvertiert

## [0.0.6] - 2025-12-11

### Sicherheit

- **KRITISCH**: Flask-Debug-Modus standardmäßig in Produktion aktiviert – behoben
  - Debug-Modus wird jetzt durch Umgebungsvariable `FLASK_DEBUG` gesteuert (Standard: false)
  - Host-Binding standardmäßig `127.0.0.1` statt `0.0.0.0`
- **HOCH**: Anfällige Abhängigkeiten aktualisiert
  - `flask-cors`: 4.0.0 → 6.0.0 (CVE-2024-1681, CVE-2024-6844, CVE-2024-6866, CVE-2024-6839)
  - `gunicorn`: 21.2.0 → 23.0.0 (CVE-2024-1135, CVE-2024-6827)
  - `werkzeug`: 3.0.1 → 3.1.4 (CVE-2024-34069, CVE-2024-49766, CVE-2024-49767, CVE-2025-66221)
- **MITTEL**: Path-Traversal-Schutz für Datei-Serving-Endpoints hinzugefügt
  - Bild-Serving validiert, dass Pfade erlaubte Verzeichnisse nicht verlassen
  - Blockiert Verzeichnis-Traversal-Sequenzen (`..`)
- **MITTEL**: Erweiterte SQL-Abfrage-Sanitisierung
  - Suchabfragen escapen jetzt LIKE-Wildcards
  - Abfragelängenlimits hinzugefügt
- Umfassendes `SECURITY.md` hinzugefügt mit:
  - Sicherheitsaudit-Zusammenfassung
  - Produktions-Deployment-Checkliste
  - Umgebungsvariablen-Dokumentation
  - Richtlinien zur Meldung von Schwachstellen

### Geändert

- Backend verwendet jetzt Umgebungsvariablen für alle sicherheitsrelevanten Konfigurationen
- Standard-Host von `0.0.0.0` auf `127.0.0.1` für sicherere Defaults geändert

## [0.0.5] - 2025-12-10

### Hinzugefügt

- **Stapelverarbeitung**: Mehrere Dateien gleichzeitig hochladen und konvertieren
  - Stapelmodus im Header umschalten
  - Mehrere Dokumente gleichzeitig verarbeiten

- **Bild- und Tabellenextraktion**:
  - Eingebettete Bilder aus Dokumenten extrahieren
  - Einzelne Bilder herunterladen
  - Tabellen mit vollständiger Datenerhaltung extrahieren
  - Tabellen als CSV exportieren
  - Tabellenvorschauen in der UI anzeigen

- **RAG/Chunking-Unterstützung**:
  - Dokumenten-Chunking für RAG-Anwendungen
  - Konfigurierbare max. Tokens pro Chunk (64-8192)
  - Merge-Peers-Option für unterdimensionierte Chunks
  - Chunks als JSON herunterladen

- **Zusätzliche Exportformate**:
  - Dokument-Tokens (`.tokens.json`)
  - RAG-Chunks (`.chunks.json`)
  - Erweiterter DocTags-Export

- **Erweiterte OCR-Optionen**:
  - Mehrere OCR-Backends: EasyOCR, Tesseract, macOS Vision, RapidOCR
  - GPU-Beschleunigungsunterstützung (EasyOCR)
  - Konfigurierbarer Konfidenzschwellenwert (0-1)
  - Bitmap-Bereichsschwellenwert-Steuerung
  - Unterstützung für 28+ Sprachen

- **Tabellenstruktur-Optionen**:
  - Schnell vs. Präzise Erkennungsmodi
  - Zellabgleich-Konfiguration
  - Strukturextraktions-Umschalter

- **Bildgenerierungs-Optionen**:
  - Seitenbilder generieren
  - Bildbilder extrahieren
  - Tabellenbilder extrahieren
  - Konfigurierbare Bildskalierung (0.1x - 4.0x)

- **Performance/Akzelerator-Optionen**:
  - Geräteauswahl: Auto, CPU, CUDA, MPS (Apple Silicon)
  - Thread-Anzahl-Konfiguration (1-32)
  - Dokument-Timeout-Einstellung

- **Neue API-Endpoints**:
  - `POST /api/convert/batch` - Stapelkonvertierung
  - `GET /api/convert/<job_id>/images` - Extrahierte Bilder auflisten
  - `GET /api/convert/<job_id>/images/<id>` - Bild herunterladen
  - `GET /api/convert/<job_id>/tables` - Extrahierte Tabellen auflisten
  - `GET /api/convert/<job_id>/tables/<id>/csv` - Tabellen-CSV herunterladen
  - `GET /api/convert/<job_id>/tables/<id>/image` - Tabellenbild herunterladen
  - `GET /api/convert/<job_id>/chunks` - Dokument-Chunks abrufen
  - `GET/PUT /api/settings/performance` - Performance-Einstellungen
  - `GET/PUT /api/settings/chunking` - Chunking-Einstellungen
  - `GET /api/settings/formats` - Alle unterstützten Formate auflisten

### Geändert

- **Einstellungs-Panel**: Vollständig neu gestaltet mit allen neuen Optionen
- **Export-Optionen**: Mit Tabs für verschiedene Inhaltstypen erweitert
- **DropZone**: Mit Formatkategorien und Stapelmodus-Unterstützung aktualisiert
- **Converter-Service**: Große Refaktorierung für dynamische Pipeline-Optionen

### Behoben

- Konfidenz-Score-Berechnung verwendet jetzt Cluster-Level-Vorhersagen
- Bessere Handhabung von teilweisem Konvertierungserfolg

## [0.0.4] - 2025-12-10

### Hinzugefügt

- **OCR-Unterstützung**: Vollständige OCR-Integration mit EasyOCR
  - Unterstützung für 14+ Sprachen
  - Option „Force Full Page OCR“
  - Konfigurierbare OCR-Einstellungen
- **Verbesserte Konfidenzberechnung**: Durchschnittliche Konfidenz aus Layout-Vorhersagen

### Geändert

- Converter-Service für konfigurierbare Pipeline-Optionen aktualisiert
- Einstellungs-Panel mit OCR-Optionen erweitert

## [0.0.3] - 2025-12-10

### Hinzugefügt

- Erste Veröffentlichung von Duckling
- **Frontend-Funktionen**:
  - Drag-and-Drop-Datei-Upload
  - Echtzeit-Konvertierungsfortschritt
  - Multi-Format-Export-Optionen
  - Einstellungs-Panel
  - Konvertierungs-History-Panel
  - Dunkles Theme mit Türkis-Akzent
  - Responsives Design
  - Animierte Übergänge

- **Backend-Funktionen**:
  - Flask-REST-API mit CORS
  - Asynchrone Dokumentenkonvertierung
  - SQLite-basierte History
  - Datei-Upload-Verwaltung
  - Konfigurierbare Einstellungen
  - Health-Check-Endpoint

- **Unterstützte Eingabeformate**:
  - PDF, Word, PowerPoint, Excel
  - HTML, Markdown, CSV
  - Bilder (PNG, JPG, TIFF usw.)
  - AsciiDoc, XML

- **Exportformate**:
  - Markdown, HTML, JSON
  - DocTags, Plain Text

- **Developer Experience**:
  - Umfassende Test-Suites
  - Docker-Unterstützung
  - TypeScript
  - ESLint-Konfiguration

### Sicherheit

- Eingabevalidierung für Datei-Uploads
- Dateityp-Einschränkungen
- Maximale Dateigrößenlimits
- Sichere Dateinamenbehandlung

[Unreleased]: https://github.com/davidgs/duckling/compare/v0.0.11...HEAD
[0.0.11]: https://github.com/davidgs/duckling/compare/v0.0.10a...v0.0.11
[0.0.10a]: https://github.com/davidgs/duckling/compare/v0.0.10...v0.0.10a
[0.0.10]: https://github.com/davidgs/duckling/compare/v0.0.9...v0.0.10
[0.0.9]: https://github.com/davidgs/duckling/compare/v0.0.8...v0.0.9
[0.0.8]: https://github.com/davidgs/duckling/compare/v0.0.7...v0.0.8
[0.0.7]: https://github.com/davidgs/duckling/compare/v0.0.6...v0.0.7
[0.0.6]: https://github.com/davidgs/duckling/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/davidgs/duckling/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/davidgs/duckling/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/davidgs/duckling/releases/tag/v0.0.3
