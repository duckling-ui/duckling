# API de conversión

Endpoints para subir y convertir documentos.

## Subir y convertir un solo documento

```http
POST /api/convert
Content-Type: multipart/form-data
```

### Parámetros

| Nombre | Tipo | Obligatorio | Descripción |
|--------|------|-------------|-------------|
| `file` | Archivo | Sí | Documento a convertir |
| `settings` | Cadena JSON | No | Sobrescritura de la configuración de conversión |

### Ejemplo de solicitud

```bash
curl -X POST http://localhost:5001/api/convert \
  -F "file=@document.pdf" \
  -F 'settings={"ocr":{"enabled":true,"language":"en"}}'
```

### Respuesta (202 Accepted)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "input_format": "pdf",
  "status": "processing",
  "message": "Conversión iniciada"
}
```

---

## Conversión por lotes de varios documentos

```http
POST /api/convert/batch
Content-Type: multipart/form-data
```

### Parámetros

| Nombre | Tipo | Obligatorio | Descripción |
|--------|------|-------------|-------------|
| `files` | Archivo[] | Sí | Documentos a convertir (repita el campo `files` en cada parte). Las subidas de carpetas desde la interfaz usan la misma forma: una parte multipart por archivo tras expandir el directorio en el navegador. |
| `settings` | Cadena JSON | No | Sobrescritura de la configuración de conversión |

**Tipos admitidos:** Cada nombre de archivo debe tener una extensión permitida por el servidor (véase `ALLOWED_EXTENSIONS` en el despliegue). Las partes no admitidas no se convierten; aparecen en la respuesta con `"status": "rejected"`. Si **todas** las partes no son compatibles (o no generan ninguna conversión), la API devuelve **400** con un mensaje `error` y la lista `jobs` por archivo.

**Tamaño de la solicitud:** Todo el cuerpo multipart debe estar dentro de `MAX_CONTENT_LENGTH` (por defecto 100 MB para toda la solicitud), no por archivo. Las carpetas grandes pueden dividirse en varias solicitudes por lotes.

### Ejemplo de solicitud

```bash
curl -X POST http://localhost:5001/api/convert/batch \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "files=@image.png"
```

### Respuesta (202 Accepted)

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
  "message": "Se iniciaron 3 conversiones"
}
```

### Respuesta (400 Bad Request)

Se devuelve cuando no se inicia ningún trabajo de conversión (por ejemplo, si todos los archivos tienen una extensión no permitida):

```json
{
  "error": "No hay archivos compatibles para convertir",
  "jobs": [
    {
      "filename": "readme.exe",
      "status": "rejected",
      "error": "Tipo de archivo no permitido"
    }
  ],
  "total": 1
}
```

---

## Convertir documento desde URL

```http
POST /api/convert/url
Content-Type: application/json
```

### Parámetros

| Nombre | Tipo | Obligatorio | Descripción |
|--------|------|-------------|-------------|
| `url` | string | Sí | URL del documento a convertir |
| `settings` | object | No | Sobrescritura de la configuración de conversión |

### Ejemplo de solicitud

```bash
curl -X POST http://localhost:5001/api/convert/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/document.pdf",
    "settings": {"ocr": {"enabled": true}}
  }'
```

### Respuesta (202 Accepted)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "source_url": "https://example.com/document.pdf",
  "input_format": "pdf",
  "status": "processing",
  "message": "Conversión iniciada"
}
```

---

## Conversión por lotes desde URLs

```http
POST /api/convert/url/batch
Content-Type: application/json
```

### Parámetros

| Nombre | Tipo | Obligatorio | Descripción |
|--------|------|-------------|-------------|
| `urls` | string[] | Sí | Lista de URLs a convertir |
| `settings` | object | No | Sobrescritura de la configuración de conversión |

### Ejemplo de solicitud

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

### Respuesta (202 Accepted)

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
      "error": "Tipo de archivo no permitido"
    }
  ],
  "total": 3,
  "message": "Se iniciaron 2 conversiones"
}
```

---

## Obtener el estado de la conversión

```http
GET /api/convert/{job_id}/status
```

### Respuesta (en proceso)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "message": "Analizando documento con OCR (easyocr, en)..."
}
```

### Respuesta (completada)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "message": "Conversión completada correctamente",
  "confidence": 0.92,
  "formats_available": ["markdown", "html", "json", "text", "doctags"],
  "images_count": 3,
  "tables_count": 2,
  "chunks_count": 0,
  "preview": "# Título del documento\n\nPrimer párrafo..."
}
```

### Respuesta (error)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "progress": 0,
  "message": "Error en la conversión: formato PDF no válido",
  "error": "Formato PDF no válido"
}
```

---

## Obtener el resultado de la conversión

```http
GET /api/convert/{job_id}/result
```

### Respuesta

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "confidence": 0.92,
  "formats_available": ["markdown", "html", "json", "text", "doctags", "document_tokens"],
  "result": {
    "markdown_preview": "# Título del documento\n\nVista previa del contenido...",
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

## Obtener imágenes extraídas

```http
GET /api/convert/{job_id}/images
```

### Respuesta

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "images": [
    {
      "id": 1,
      "filename": "image_1.png",
      "path": "/outputs/job_id/images/image_1.png",
      "caption": "Figura 1: diagrama de arquitectura",
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

## Descargar imagen extraída

```http
GET /api/convert/{job_id}/images/{image_id}
```

**Respuesta:** Archivo de imagen binario (PNG)

---

## Obtener tablas extraídas

```http
GET /api/convert/{job_id}/tables
```

### Respuesta

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "tables": [
    {
      "id": 1,
      "label": "table",
      "caption": "Tabla 1: datos de ventas",
      "rows": [
        ["Producto", "T1", "T2", "T3", "T4"],
        ["Artículo A", "100", "150", "200", "175"]
      ],
      "csv_path": "/outputs/job_id/tables/table_1.csv",
      "image_path": "/outputs/job_id/tables/table_1.png"
    }
  ],
  "count": 1
}
```

---

## Descargar tabla en CSV

```http
GET /api/convert/{job_id}/tables/{table_id}/csv
```

**Respuesta:** Archivo CSV

---

## Descargar tabla como imagen

```http
GET /api/convert/{job_id}/tables/{table_id}/image
```

**Respuesta:** Archivo de imagen binario (PNG)

---

## Obtener fragmentos del documento

```http
GET /api/convert/{job_id}/chunks
```

### Respuesta

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": [
    {
      "id": 1,
      "text": "Primer fragmento de texto del documento.",
      "meta": {
        "headings": ["Introducción"],
        "page": 1
      }
    },
    {
      "id": 2,
      "text": "Segundo fragmento continúa el contenido.",
      "meta": {
        "headings": ["Introducción", "Antecedentes"],
        "page": 1
      }
    }
  ],
  "count": 2
}
```

---

## Exportar documento

```http
GET /api/export/{job_id}/{format}
```

### Formatos admitidos

- `markdown`
- `html`
- `json`
- `text`
- `doctags`
- `document_tokens`
- `chunks`

**Respuesta:** Descarga de archivo con el tipo MIME adecuado

---

## Eliminar trabajo

```http
DELETE /api/convert/{job_id}
```

### Respuesta

```json
{
  "message": "Trabajo 550e8400-e29b-41d4-a716-446655440000 eliminado",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```
