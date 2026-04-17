# API del historial

Endpoints para acceder al historial de conversiones.

## Obtener el historial de conversiones

```http
GET /api/history
```

### Parámetros de consulta

| Nombre | Tipo | Predeterminado | Descripción |
|--------|------|----------------|-------------|
| `limit` | int | 50 | Número máximo de entradas a devolver |
| `offset` | int | 0 | Número de entradas a omitir |
| `status` | string | - | Filtrar por estado |

### Respuesta

```json
{
  "entries": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document_abc123.pdf",
      "original_filename": "Mi documento.pdf",
      "input_format": "pdf",
      "status": "completed",
      "confidence": 0.92,
      "file_size": 1048576,
      "created_at": "2024-01-15T10:00:00Z",
      "completed_at": "2024-01-15T10:00:30Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

## Obtener el historial reciente

```http
GET /api/history/recent
```

### Parámetros de consulta

| Nombre | Tipo | Predeterminado | Descripción |
|--------|------|----------------|-------------|
| `limit` | int | 10 | Número máximo de entradas a devolver |

---

## Obtener una entrada del historial

```http
GET /api/history/{job_id}
```

### Respuesta

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document_abc123.pdf",
  "original_filename": "Mi documento.pdf",
  "input_format": "pdf",
  "status": "completed",
  "confidence": 0.92,
  "error_message": null,
  "output_path": "/outputs/550e8400.../document.md",
  "document_json_path": "/outputs/550e8400.../document.json",
  "settings": {
    "ocr": {"enabled": true}
  },
  "file_size": 1048576,
  "created_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:00:30Z"
}
```

---

## Cargar un document desde el historial

```http
GET /api/history/{job_id}/load
```

Carga un documento convertido previamente desde el historial y lo devuelve como resultado de conversión. Este endpoint carga el `DoclingDocument` desde el archivo JSON almacenado y lo devuelve en el mismo formato que un resultado de conversión recién obtenido.

### Parámetros de ruta

| Nombre | Tipo | Obligatorio | Descripción |
|--------|------|-------------|-------------|
| `job_id` | string | Sí | Identificador del trabajo (debe coincidir con `[A-Za-z0-9_-]+`) |

### Respuesta

Devuelve un objeto `ConversionResult` con el mismo formato que una conversión nueva:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "document": {
    "title": "Mi documento",
    "content": "...",
    "metadata": {...}
  },
  "formats_available": ["markdown", "html", "json"],
  "images_count": 5,
  "tables_count": 2,
  "preview": "# Vista previa del contenido del documento..."
}
```

### Respuestas de error

**404 Not Found**: la entrada del historial no existe
```json
{
  "error": "Entrada de historial {job_id} no encontrada"
}
```

**400 Bad Request**: conversión no completada
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Conversión no completada"
}
```

### Notas

- Solo funciona para conversiones completadas
- Si el archivo JSON del documento almacenado no está disponible, el endpoint intentará reconstruir el resultado a partir de los archivos de salida
- Los documentos se almacenan automáticamente tras cada conversión correcta
- El campo `document_json_path` en las entradas del historial indica dónde se guarda el JSON del documento

---

## Reconciliar el historial con el disco

```http
POST /api/history/reconcile
```

Explora el directorio de salida en busca de resultados de conversión que existen en disco pero no tienen entrada en la base de datos (p. ej., tras pérdida de la BD o reinicio). Crea las entradas de historial faltantes para que aparezcan en la interfaz y puedan volver a cargarse.

La reconciliación también se ejecuta automáticamente al iniciar la aplicación.

### Respuesta

```json
{
  "message": "Se reconciliaron 3 entradas desde el disco",
  "added_count": 3,
  "added_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ]
}
```

### Notas

- Solo se reconcilian directorios de salida con nombres UUID válidos y al menos un archivo de salida (`.md`, `.html`, `.json` o `.document.json`)
- Las entradas que ya están en la base de datos se omiten

---

## Generar fragmentos (chunks)

```http
POST /api/history/{job_id}/generate-chunks
```

Genera fragmentos RAG para un documento completado bajo demanda. Carga el DoclingDocument desde disco, aplica la configuración actual de fragmentación y devuelve los fragmentos generados. Guarda los fragmentos en disco para su descarga.

### Respuesta

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": [
    {
      "id": 1,
      "text": "Contenido del fragmento...",
      "meta": { "page": 1, "headings": ["Título de sección"] }
    }
  ],
  "count": 42
}
```

**404 Not Found**: entrada del historial o documento no encontrado

---

## Eliminar una entrada del historial

```http
DELETE /api/history/{job_id}
```

### Respuesta

```json
{
  "message": "Entrada eliminada",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Obtener estadísticas del historial

```http
GET /api/history/stats
```

### Respuesta

Devuelve estadísticas de conversión, uso de almacenamiento y profundidad de la cola. El objeto `conversions` incluye métricas ampliadas cuando están disponibles.

```json
{
  "conversions": {
    "total": 150,
    "completed": 142,
    "failed": 5,
    "pending": 2,
    "processing": 1,
    "success_rate": 94.7,
    "format_breakdown": {
      "pdf": 100,
      "docx": 30,
      "image": 20
    },
    "avg_processing_seconds": 12.5,
    "ocr_backend_breakdown": {
      "easyocr": 80,
      "ocrmac": 50,
      "tesseract": 20
    },
    "output_format_breakdown": {
      "markdown": 150
    },
    "performance_device_breakdown": {
      "auto": 120,
      "cpu": 30
    },
    "chunking_enabled_count": 25,
    "error_category_breakdown": {
      "ocr": 2,
      "other": 3
    },
    "source_type_breakdown": {
      "upload": 100,
      "url": 30,
      "batch": 20
    }
  },
  "storage": {
    "uploads": { "count": 10, "size_bytes": 1048576, "size_mb": 1.0 },
    "outputs": { "count": 140, "size_bytes": 52428800, "size_mb": 50.0 },
    "total_size_mb": 51.0
  },
  "queue_depth": 2
}
```

---

## Buscar en el historial

```http
GET /api/history/search
```

### Parámetros de consulta

| Nombre | Tipo | Obligatorio | Descripción |
|--------|------|-------------|-------------|
| `q` | string | Sí | Consulta de búsqueda |
| `limit` | int | No | Número máximo de resultados (predeterminado: 20) |

### Respuesta

```json
{
  "entries": [...],
  "query": "factura",
  "count": 5
}
```

---

## Exportar el historial

```http
GET /api/history/export
```

**Respuesta**: descarga de un archivo JSON con todas las entradas del historial

---

## Borrar todo el historial

```http
DELETE /api/history
```

### Respuesta

```json
{
  "message": "Se eliminaron todas las entradas del historial",
  "count": 150
}
```
