# Duckling

Eine moderne, benutzerfreundliche Web-Oberfläche für [Docling](https://github.com/docling-project/docling) (IBM) – eine leistungsstarke Bibliothek zur Dokumentkonvertierung.

![Duckling Screenshot](../screenshot.png)

## Überblick

Duckling bietet eine intuitive Web-Oberfläche, um Dokumente mit Docling zu konvertieren. Ob du Text aus PDFs extrahieren, Word-Dokumente nach Markdown konvertieren oder OCR für gescannte Bilder nutzen möchtest: Duckling macht es einfach.

## Schnellstart

Siehe **Getting Started**, um Duckling mit Docker oder lokal in der Entwicklung zu installieren und auszuführen.

## Übersetzungsstatus

Die deutsche Dokumentation ist in Arbeit. Einige Seiten können vorläufig oder nur teilweise übersetzt sein.



    ```bash
    # Repository klonen
    git clone https://github.com/davidgs/duckling.git
    cd duckling

    # Backend-Einrichtung
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python duckling.py

    # Frontend-Einrichtung (neues Terminal)
    cd frontend
    npm install
    npm run dev
    ```

Greifen Sie auf die Anwendung unter `http://localhost:3000` zu

## Unterstützte Formate

### Eingabeformate

| Format | Erweiterungen | Beschreibung |
|--------|---------------|--------------|
| PDF | `.pdf` | Portable Document Format |
| Word | `.docx` | Microsoft Word-Dokumente |
| PowerPoint | `.pptx` | Microsoft PowerPoint-Präsentationen |
| Excel | `.xlsx` | Microsoft Excel-Tabellenkalkulationen |
| HTML | `.html`, `.htm` | Webseiten |
| Markdown | `.md`, `.markdown` | Markdown-Dateien |
| Bilder | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.gif`, `.webp`, `.bmp` | Direkte Bild-OCR |
| AsciiDoc | `.asciidoc`, `.adoc` | Technische Dokumentation |
| PubMed XML | `.xml` | Wissenschaftliche Artikel |
| USPTO XML | `.xml` | Patentdokumente |

### Exportformate

| Format | Erweiterung | Beschreibung |
|--------|-------------|--------------|
| Markdown | `.md` | Formatierter Text mit Überschriften, Listen, Links |
| HTML | `.html` | Web-fertiges Format mit Styling |
| JSON | `.json` | Vollständige Dokumentstruktur |
| Klartext | `.txt` | Einfacher Text ohne Formatierung |
| DocTags | `.doctags` | Markiertes Dokumentformat |
| Document Tokens | `.tokens.json` | Token-Ebene-Darstellung |
| RAG Chunks | `.chunks.json` | Chunks für RAG-Anwendungen |

## Architektur

```mermaid
graph LR
    A[Browser] --> B[React Frontend]
    B --> C[Flask Backend]
    C --> D[Docling Engine]
    D --> E[(Storage)]

    style A fill:#3b82f6,color:#fff
    style B fill:#1e3a5f,color:#fff
    style C fill:#14b8a6,color:#fff
    style D fill:#8b5cf6,color:#fff
    style E fill:#f59e0b,color:#fff
```

## Dokumentation

- **[Erste Schritte](getting-started/index.md)** - Installations- und Schnellstartanleitung
- **[Benutzerhandbuch](user-guide/index.md)** - Funktionen und Konfigurationsoptionen
- **[API-Referenz](api/index.md)** - Vollständige API-Dokumentation
- **[Architektur](architecture/index.md)** - Systemdesign und Komponenten
- **[Bereitstellung](deployment/index.md)** - Produktionsbereitstellungsanleitung
- **[Mitwirken](contributing/index.md)** - Wie man beiträgt## Danksagungen- [Docling](https://github.com/docling-project/docling) von IBM für die leistungsstarke Dokumentkonvertierungs-Engine
- [React](https://react.dev/) für das Frontend-Framework
- [Flask](https://flask.palletsprojects.com/) für das Backend-Framework
- [Tailwind CSS](https://tailwindcss.com/) für das Styling
- [Framer Motion](https://www.framer.com/motion/) für Animationen
