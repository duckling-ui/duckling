# Formatos admitidos

Referencia completa de los formatos de entrada y salida que admite Duckling.

## Formatos de entrada

### Documentos

| Formato | Extensiones | Descripción | Notas |
|---------|-------------|-------------|-------|
| PDF | `.pdf` | Portable Document Format | Soporte completo, incluidos PDF escaneados con OCR |
| Word | `.docx` | Microsoft Word | Solo formato moderno (no `.doc`) |
| PowerPoint | `.pptx` | Microsoft PowerPoint | Extrae texto e imágenes de las diapositivas |
| Excel | `.xlsx` | Microsoft Excel | Extrae tablas y datos |
| HTML | `.html`, `.htm` | Páginas web | Conserva estructura y formato |
| Markdown | `.md`, `.markdown` | Archivos Markdown | Soporte completo de CommonMark |

### Imágenes

| Formato | Extensiones | Descripción | Notas |
|---------|-------------|-------------|-------|
| PNG | `.png` | Portable Network Graphics | Ideal para capturas y diagramas |
| JPEG | `.jpg`, `.jpeg` | Joint Photographic Experts Group | Ideal para fotos |
| TIFF | `.tiff`, `.tif` | Tagged Image File Format | Soporte multipágina |
| GIF | `.gif` | Graphics Interchange Format | Solo el primer fotograma |
| WebP | `.webp` | Web Picture format | Formato web moderno |
| BMP | `.bmp` | Bitmap | Imágenes sin comprimir |

### Documentos técnicos

| Formato | Extensiones | Descripción | Notas |
|---------|-------------|-------------|-------|
| AsciiDoc | `.asciidoc`, `.adoc` | Documentación técnica | Sintaxis AsciiDoc completa |
| PubMed XML | `.xml` | Artículos científicos | Formato PubMed Central |
| USPTO XML | `.xml` | Patentes | Formato de patentes de EE. UU. |

## Formatos de salida

### Formatos de texto

#### Markdown (`.md`)

Lo mejor para documentación y contenido que necesita formato.

```markdown
# Título del documento

## Sección 1

Este es un párrafo con texto en **negrita** y en *cursiva*.

- Elemento de lista 1
- Elemento de lista 2

| Columna 1 | Columna 2 |
|-----------|-----------|
| Dato 1    | Dato 2    |
```

#### HTML (`.html`)

Formato listo para la web con estilos conservados.

```html
<h1>Título del documento</h1>
<h2>Sección 1</h2>
<p>Este es un párrafo con texto en <strong>negrita</strong> y en <em>cursiva</em>.</p>
```

#### Texto plano (`.txt`)

Texto simple sin formato.

```
Título del documento

Sección 1

Este es un párrafo con texto en negrita y en cursiva.
```

### Formatos estructurados

#### JSON (`.json`)

Estructura completa del documento en JSON. Representación sin pérdida.

```json
{
  "title": "Título del documento",
  "sections": [
    {
      "heading": "Sección 1",
      "level": 2,
      "content": [
        {
          "type": "paragraph",
          "text": "Este es un párrafo..."
        }
      ]
    }
  ]
}
```

#### DocTags (`.doctags`)

Formato de documento etiquetado para análisis semántico.

```
<document>
  <title>Título del documento</title>
  <section level="2">
    <heading>Sección 1</heading>
    <paragraph>Este es un párrafo...</paragraph>
  </section>
</document>
```

#### DocLang (`.dclg.xml`)

Formato XML de documento nativo para IA del [estándar abierto DocLang](https://doclang.ai). Duckling exporta DocLang mediante la API `export_to_doclang()` de Docling. El formato preserva estructura, roles semánticos, diseño y geometría de cuadros delimitadores para pipelines de LLM y agentes.

```xml
<doclang>
  <heading level="1">
    <location value="48"/><location value="40"/>
    <location value="420"/><location value="72"/>
    Título del documento
  </heading>
  <text>Este es un párrafo...</text>
  <table>
    <ched/>Columna 1<ched/>Columna 2<nl/>
    <fcel/>Dato 1<fcel/>Dato 2<nl/>
  </table>
</doclang>
```

Requiere Docling 2.70.0 o superior (véase `backend/requirements.txt`).

#### Document Tokens (`.tokens.json`)

Representación a nivel de tokens para aplicaciones de PLN.

```json
{
  "tokens": [
    {"text": "Documento", "type": "word", "position": 0},
    {"text": "Título", "type": "word", "position": 1}
  ]
}
```

### Formatos RAG

#### RAG Chunks (`.chunks.json`)

Fragmentos de documento optimizados para generación aumentada por recuperación (RAG).

```json
{
  "chunks": [
    {
      "id": 1,
      "text": "Este es el primer fragmento de texto...",
      "meta": {
        "headings": ["Sección 1"],
        "page": 1,
        "token_count": 128
      }
    }
  ]
}
```

## Guía de selección de formato

| Caso de uso | Formato recomendado |
|-------------|---------------------|
| Documentación | Markdown |
| Publicación web | HTML |
| Procesamiento de datos | JSON |
| Indexación de búsqueda | Texto plano |
| Pipelines de PLN / ML | Document Tokens |
| Aplicaciones RAG | RAG Chunks |
| Análisis semántico | DocTags |
| Intercambio nativo IA / RAG empresarial | DocLang |

## Parámetro de formato de la API

Al usar la API, indique el formato en el punto final de exportación:

```bash
# Descargar como Markdown
curl http://localhost:5001/api/export/{job_id}/markdown

# Descargar como JSON
curl http://localhost:5001/api/export/{job_id}/json

# Descargar como HTML
curl http://localhost:5001/api/export/{job_id}/html

# Descargar como DocLang
curl http://localhost:5001/api/export/{job_id}/doclang
```

## Tipos MIME

| Formato | Tipo MIME |
|---------|-----------|
| Markdown | `text/markdown` |
| HTML | `text/html` |
| JSON | `application/json` |
| Texto plano | `text/plain` |
| DocTags | `application/xml` |
| DocLang | `application/xml` |
