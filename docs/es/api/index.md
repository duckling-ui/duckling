# Referencia de la API

Documentación completa de la API backend de Duckling.

## URL base

```
http://localhost:5001/api
```

## Autenticación

Por ahora la API no requiere autenticación. En entornos de producción, considere añadir un middleware de autenticación.

## Secciones

<div class="grid cards" markdown>

-   :material-file-document-multiple:{ .lg .middle } __Conversión__

    ---

    Subir y convertir documentos

    [:octicons-arrow-right-24: API de conversión](conversion.md)

-   :material-cog:{ .lg .middle } __Configuración__

    ---

    Obtener y actualizar la configuración

    [:octicons-arrow-right-24: API de configuración](settings.md)

-   :material-history:{ .lg .middle } __Historial__

    ---

    Acceder al historial de conversiones

    [:octicons-arrow-right-24: API de historial](history.md)

</div>

## Referencia rápida

### Endpoints de conversión

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/convert` | POST | Subir y convertir un documento |
| `/convert/batch` | POST | Convertir varios documentos por lotes |
| `/convert/{job_id}/status` | GET | Obtener el estado de la conversión |
| `/convert/{job_id}/result` | GET | Obtener el resultado de la conversión |
| `/convert/{job_id}/images` | GET | Listar imágenes extraídas |
| `/convert/{job_id}/images/{id}` | GET | Descargar una imagen extraída |
| `/convert/{job_id}/tables` | GET | Listar tablas extraídas |
| `/convert/{job_id}/tables/{id}/csv` | GET | Descargar tabla como CSV |
| `/convert/{job_id}/chunks` | GET | Obtener fragmentos del documento |
| `/export/{job_id}/{format}` | GET | Descargar el archivo convertido |

### Endpoints de configuración

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/settings` | GET/PUT | Obtener/actualizar todos los ajustes |
| `/settings/reset` | POST | Restablecer valores predeterminados |
| `/settings/formats` | GET | Listar formatos admitidos |
| `/settings/ocr` | GET/PUT | Ajustes de OCR |
| `/settings/tables` | GET/PUT | Ajustes de tablas |
| `/settings/images` | GET/PUT | Ajustes de imágenes |
| `/settings/performance` | GET/PUT | Ajustes de rendimiento |
| `/settings/chunking` | GET/PUT | Ajustes de fragmentación (chunks) |

### Endpoints de historial

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/history` | GET | Listar historial de conversiones |
| `/history/{job_id}` | GET | Obtener una entrada del historial |
| `/history/stats` | GET | Obtener estadísticas de conversión |
| `/history/search` | GET | Buscar en el historial |

## Comprobación de estado (Health Check)

```http
GET /health
```

**Respuesta**

```json
{
  "status": "healthy",
  "service": "duckling-backend"
}
```

## Respuestas de error

Todos los endpoints pueden devolver errores con el siguiente formato:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### Códigos de estado HTTP

| Código | Descripción |
|------|-------------|
| 200 | Éxito |
| 202 | Aceptado (operación asíncrona iniciada) |
| 400 | Solicitud incorrecta (entrada no válida) |
| 404 | No encontrado |
| 413 | Carga útil demasiado grande |
| 500 | Error interno del servidor |

## Limitación de velocidad

No hay limitación de velocidad implementada por el momento. En producción, considere añadir un middleware de limitación.

## CORS

La API permite solicitudes entre orígenes desde el origen del frontend configurado (predeterminado: `http://localhost:3000`).
