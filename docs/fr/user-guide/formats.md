# Formats pris en charge

Référence complète des formats d’entrée et de sortie pris en charge par Duckling.

## Formats d’entrée

### Documents

| Format | Extensions | Description | Remarques |
|--------|------------|-------------|-----------|
| PDF | `.pdf` | Portable Document Format | Prise en charge complète, y compris les PDF numérisés avec OCR |
| Word | `.docx` | Microsoft Word | Format moderne uniquement (pas `.doc`) |
| PowerPoint | `.pptx` | Microsoft PowerPoint | Extrait le texte et les images des diapositives |
| Excel | `.xlsx` | Microsoft Excel | Extrait les tableaux et les données |
| HTML | `.html`, `.htm` | Pages web | Préserve la structure et la mise en forme |
| Markdown | `.md`, `.markdown` | Fichiers Markdown | Prise en charge complète de CommonMark |

### Images

| Format | Extensions | Description | Remarques |
|--------|------------|-------------|-----------|
| PNG | `.png` | Portable Network Graphics | Idéal pour captures et schémas |
| JPEG | `.jpg`, `.jpeg` | Joint Photographic Experts Group | Idéal pour les photos |
| TIFF | `.tiff`, `.tif` | Tagged Image File Format | Prise en charge multipage |
| GIF | `.gif` | Graphics Interchange Format | Première image uniquement |
| WebP | `.webp` | Web Picture format | Format web moderne |
| BMP | `.bmp` | Bitmap | Images non compressées |

### Documents techniques

| Format | Extensions | Description | Remarques |
|--------|------------|-------------|-----------|
| AsciiDoc | `.asciidoc`, `.adoc` | Documentation technique | Syntaxe AsciiDoc complète |
| PubMed XML | `.xml` | Articles scientifiques | Format PubMed Central |
| USPTO XML | `.xml` | Brevets | Format des brevets américains |

## Formats de sortie

### Formats texte

#### Markdown (`.md`)

Idéal pour la documentation et les contenus nécessitant une mise en forme.

```markdown
# Titre du document

## Section 1

Ceci est un paragraphe avec du texte en **gras** et en *italique*.

- Élément de liste 1
- Élément de liste 2

| Colonne 1 | Colonne 2 |
|-----------|-----------|
| Donnée 1  | Donnée 2  |
```

#### HTML (`.html`)

Format prêt pour le web avec styles conservés.

```html
<h1>Titre du document</h1>
<h2>Section 1</h2>
<p>Ceci est un paragraphe avec du texte en <strong>gras</strong> et en <em>italique</em>.</p>
```

#### Texte brut (`.txt`)

Texte simple sans mise en forme.

```
Titre du document

Section 1

Ceci est un paragraphe avec du texte en gras et en italique.
```

### Formats structurés

#### JSON (`.json`)

Structure complète du document au format JSON. Représentation sans perte.

```json
{
  "title": "Titre du document",
  "sections": [
    {
      "heading": "Section 1",
      "level": 2,
      "content": [
        {
          "type": "paragraph",
          "text": "Ceci est un paragraphe..."
        }
      ]
    }
  ]
}
```

#### DocTags (`.doctags`)

Format de document balisé pour l’analyse sémantique.

```
<document>
  <title>Titre du document</title>
  <section level="2">
    <heading>Section 1</heading>
    <paragraph>Ceci est un paragraphe...</paragraph>
  </section>
</document>
```

#### Document Tokens (`.tokens.json`)

Représentation au niveau des jetons pour les applications NLP.

```json
{
  "tokens": [
    {"text": "Document", "type": "word", "position": 0},
    {"text": "Titre", "type": "word", "position": 1}
  ]
}
```

### Formats RAG

#### RAG Chunks (`.chunks.json`)

Fragments de document optimisés pour la génération augmentée par récupération (RAG).

```json
{
  "chunks": [
    {
      "id": 1,
      "text": "Ceci est le premier fragment de texte...",
      "meta": {
        "headings": ["Section 1"],
        "page": 1,
        "token_count": 128
      }
    }
  ]
}
```

## Guide du choix de format

| Cas d’usage | Format recommandé |
|-------------|-------------------|
| Documentation | Markdown |
| Publication web | HTML |
| Traitement de données | JSON |
| Indexation de recherche | Texte brut |
| Pipelines NLP / ML | Document Tokens |
| Applications RAG | RAG Chunks |
| Analyse sémantique | DocTags |

## Paramètre de format de l’API

Lors de l’utilisation de l’API, indiquez le format dans le point de terminaison d’export :

```bash
# Télécharger en Markdown
curl http://localhost:5001/api/export/{job_id}/markdown

# Télécharger en JSON
curl http://localhost:5001/api/export/{job_id}/json

# Télécharger en HTML
curl http://localhost:5001/api/export/{job_id}/html
```

## Types MIME

| Format | Type MIME |
|--------|-----------|
| Markdown | `text/markdown` |
| HTML | `text/html` |
| JSON | `application/json` |
| Texte brut | `text/plain` |
| DocTags | `application/xml` |
