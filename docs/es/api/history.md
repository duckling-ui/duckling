# Historial (API)

Endpoints para acceder al historial de conversiones.

## Obtener historial de conversiones

```http
GET /api/history
```

### Parámetros de consulta

| Nombre | Tipo | Por defecto | Descripción |
|--------|------|-------------|-------------|
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
      "original_filename": "Mi Documento.pdf",
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

## Obtener historial reciente

```http
GET /api/history/recent
```

### Parámetros de consulta

| Nombre | Tipo | Por defecto | Descripción |
|--------|------|-------------|-------------|
| `limit` | int | 10 | Número máximo de entradas a devolver |

---

## Obtener entrada del historial

```http
GET /api/history/{job_id}
```

### Respuesta

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document_abc123.pdf",
  "original_filename": "Mi Documento.pdf",
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

## Cargar documento desde el historial

```http
GET /api/history/{job_id}/load
```

Carga un documento previamente convertido desde el historial y lo devuelve como un resultado de conversión. Este endpoint carga el `DoclingDocument` desde el archivo JSON almacenado y lo devuelve en el mismo formato que un resultado de conversión nuevo.

### Parámetros de ruta

| Nombre | Tipo | Requerido | Descripción |
|--------|------|-----------|-------------|
| `job_id` | string | Sí | El identificador del trabajo (debe coincidir con `[A-Za-z0-9_-]+`) |

### Respuesta

Devuelve un objeto `ConversionResult` que coincide con el formato de una conversión nueva:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "document": {
    "title": "Mi Documento",
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

**404 Not Found**: La entrada del historial no existe
```json
{
  "error": "History entry {job_id} not found"
}
```

**400 Bad Request**: Conversión no completada
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Conversion not completed"
}
```

### Notas

- Solo funciona para conversiones completadas
- Si el archivo JSON del documento almacenado no está disponible, el endpoint intentará reconstruir el resultado desde los archivos de salida
- Los documentos se almacenan automáticamente después de cada conversión exitosa
- El campo `document_json_path` en las entradas del historial indica dónde se almacena el JSON del documento

---

## Reconciliar historial desde disco

```http
POST /api/history/reconcile
```

Escanea el directorio de salida en busca de conversiones que existen en disco pero no tienen entrada en la base de datos (p. ej. tras pérdida o reinicio de la base). Crea las entradas faltantes para que aparezcan en la interfaz y puedan recargarse.

La reconciliación también se ejecuta automáticamente al iniciar la aplicación.

### Respuesta

```json
{
  "message": "Reconciled 3 entries from disk",
  "added_count": 3,
  "added_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ]
}
```

### Notas

- Solo se reconcilian los directorios de salida con nombres UUID válidos y al menos un archivo de salida (`.md`, `.html`, `.json` o `.document.json`)
- Las entradas ya presentes en la base de datos se omiten

---

## Eliminar entrada del historial

```http
DELETE /api/history/{job_id}
```

### Respuesta

```json
{
  "message": "Entry deleted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Obtener estadísticas del historial

```http
GET /api/history/stats
```

### Respuesta

```json
{
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
  }
}
```

---

## Buscar en el historial

```http
GET /api/history/search
```

### Parámetros de consulta

| Nombre | Tipo | Requerido | Descripción |
|--------|------|-----------|-------------|
| `q` | string | Sí | Consulta de búsqueda |
| `limit` | int | No | Resultados máximos (por defecto: 20) |

### Respuesta

```json
{
  "entries": [...],
  "query": "invoice",
  "count": 5
}
```

---

## Exportar historial

```http
GET /api/history/export
```

**Respuesta**: Descarga de archivo JSON con todas las entradas del historial

---

## Limpiar todo el historial

```http
DELETE /api/history
```

### Respuesta

```json
{
  "message": "All history entries deleted",
  "count": 150
}
```
