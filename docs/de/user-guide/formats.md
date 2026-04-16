# Unterstützte Formate

Vollständige Referenz zu den von Duckling unterstützten Eingabe- und Ausgabeformaten.

## Eingabeformate

### Dokumente

| Format | Erweiterungen | Beschreibung | Hinweise |
|--------|---------------|--------------|----------|
| PDF | `.pdf` | Portable Document Format | Volle Unterstützung inkl. gescannter PDFs mit OCR |
| Word | `.docx` | Microsoft Word | Nur modernes Format (kein `.doc`) |
| PowerPoint | `.pptx` | Microsoft PowerPoint | Extrahiert Text und Bilder aus Folien |
| Excel | `.xlsx` | Microsoft Excel | Extrahiert Tabellen und Daten |
| HTML | `.html`, `.htm` | Webseiten | Struktur und Formatierung bleiben erhalten |
| Markdown | `.md`, `.markdown` | Markdown-Dateien | Volle CommonMark-Unterstützung |

### Bilder

| Format | Erweiterungen | Beschreibung | Hinweise |
|--------|---------------|--------------|----------|
| PNG | `.png` | Portable Network Graphics | Gut für Screenshots und Diagramme |
| JPEG | `.jpg`, `.jpeg` | Joint Photographic Experts Group | Gut für Fotos |
| TIFF | `.tiff`, `.tif` | Tagged Image File Format | Mehrseitige Bilder |
| GIF | `.gif` | Graphics Interchange Format | Nur erstes Einzelbild |
| WebP | `.webp` | Web Picture Format | Modernes Webformat |
| BMP | `.bmp` | Bitmap | Unkomprimierte Bilder |

### Technische Dokumente

| Format | Erweiterungen | Beschreibung | Hinweise |
|--------|---------------|--------------|----------|
| AsciiDoc | `.asciidoc`, `.adoc` | Technische Dokumentation | Volle AsciiDoc-Syntax |
| PubMed XML | `.xml` | Wissenschaftliche Artikel | PubMed Central-Format |
| USPTO XML | `.xml` | Patentschriften | US-Patentformat |

## Ausgabeformate

### Textformate

#### Markdown (`.md`)

Am besten für Dokumentation und Inhalte, die Formatierung brauchen.

```markdown
# Dokumenttitel

## Abschnitt 1

Dies ist ein Absatz mit **fettem** und *kursivem* Text.

- Listenpunkt 1
- Listenpunkt 2

| Spalte 1 | Spalte 2 |
|----------|----------|
| Daten 1  | Daten 2  |
```

#### HTML (`.html`)

Webtaugliches Format mit erhaltenem Styling.

```html
<h1>Dokumenttitel</h1>
<h2>Abschnitt 1</h2>
<p>Dies ist ein Absatz mit <strong>fettem</strong> und <em>kursivem</em> Text.</p>
```

#### Klartext (`.txt`)

Einfacher Text ohne Formatierung.

```
Dokumenttitel

Abschnitt 1

Dies ist ein Absatz mit fettem und kursivem Text.
```

### Strukturierte Formate

#### JSON (`.json`)

Vollständige Dokumentstruktur als JSON. Verlustfreie Darstellung.

```json
{
  "title": "Dokumenttitel",
  "sections": [
    {
      "heading": "Abschnitt 1",
      "level": 2,
      "content": [
        {
          "type": "paragraph",
          "text": "Dies ist ein Absatz..."
        }
      ]
    }
  ]
}
```

#### DocTags (`.doctags`)

Getaggtes Dokumentformat für semantische Analyse.

```
<document>
  <title>Dokumenttitel</title>
  <section level="2">
    <heading>Abschnitt 1</heading>
    <paragraph>Dies ist ein Absatz...</paragraph>
  </section>
</document>
```

#### Document Tokens (`.tokens.json`)

Token-Ebene für NLP-Anwendungen.

```json
{
  "tokens": [
    {"text": "Dokument", "type": "word", "position": 0},
    {"text": "Titel", "type": "word", "position": 1}
  ]
}
```

### RAG-Formate

#### RAG Chunks (`.chunks.json`)

Dokument-Chunks für Retrieval-Augmented Generation optimiert.

```json
{
  "chunks": [
    {
      "id": 1,
      "text": "Dies ist der erste Text-Chunk...",
      "meta": {
        "headings": ["Abschnitt 1"],
        "page": 1,
        "token_count": 128
      }
    }
  ]
}
```

## Formatwahl

| Anwendungsfall | Empfohlenes Format |
|----------------|-------------------|
| Dokumentation | Markdown |
| Webpublikation | HTML |
| Datenverarbeitung | JSON |
| Suchindexierung | Klartext |
| NLP-/ML-Pipelines | Document Tokens |
| RAG-Anwendungen | RAG Chunks |
| Semantische Analyse | DocTags |

## API-Formatparameter

Bei Nutzung der API geben Sie das Format im Export-Endpunkt an:

```bash
# Als Markdown herunterladen
curl http://localhost:5001/api/export/{job_id}/markdown

# Als JSON herunterladen
curl http://localhost:5001/api/export/{job_id}/json

# Als HTML herunterladen
curl http://localhost:5001/api/export/{job_id}/html
```

## MIME-Typen

| Format | MIME-Typ |
|--------|----------|
| Markdown | `text/markdown` |
| HTML | `text/html` |
| JSON | `application/json` |
| Klartext | `text/plain` |
| DocTags | `application/xml` |
