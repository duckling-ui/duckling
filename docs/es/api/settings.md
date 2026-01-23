# Configuración (API)

Endpoints para gestionar la configuración de conversión.

!!! note "Almacenamiento Basado en Sesiones"
    Los ajustes se almacenan por sesión de usuario en la base de datos. Los ajustes de cada usuario están aislados y no afectan a otros usuarios, lo que hace que Duckling sea seguro para despliegues multi-usuario.

## Obtener Todas las Configuraciones

```http
GET /api/settings
```

### Respuesta

```json
{
  "ocr": {
    "enabled": true,
    "language": "en",
    "force_full_page_ocr": false,
    "backend": "easyocr",
    "use_gpu": false,
    "confidence_threshold": 0.5,
    "bitmap_area_threshold": 0.05
  },
  "tables": {
    "enabled": true,
    "structure_extraction": true,
    "mode": "accurate",
    "do_cell_matching": true
  },
  "images": {
    "extract": true,
    "classify": true,
    "generate_page_images": false,
    "generate_picture_images": true,
    "generate_table_images": true,
    "images_scale": 1.0
  },
  "enrichment": {
    "code_enrichment": false,
    "formula_enrichment": false,
    "picture_classification": false,
    "picture_description": false
  },
  "output": {
    "default_format": "markdown"
  },
  "performance": {
    "device": "auto",
    "num_threads": 4,
    "document_timeout": null
  },
  "chunking": {
    "enabled": false,
    "max_tokens": 512,
    "merge_peers": true
  }
}
```

---

## Actualizar Configuración

```http
PUT /api/settings
Content-Type: application/json
```

### Cuerpo de la Solicitud

```json
{
  "ocr": {
    "language": "de",
    "backend": "tesseract"
  },
  "tables": {
    "mode": "fast"
  }
}
```

### Respuesta

Devuelve el objeto de configuración actualizado.

---

## Restablecer Configuración a Valores Predeterminados

```http
POST /api/settings/reset
```

### Respuesta

Devuelve el objeto de configuración predeterminado.

---

## Obtener Formatos Soportados

```http
GET /api/settings/formats
```

### Respuesta

```json
{
  "input_formats": [
    {"id": "pdf", "name": "Documento PDF", "extensions": [".pdf"], "icon": "document"},
    {"id": "docx", "name": "Microsoft Word", "extensions": [".docx"], "icon": "document"},
    {"id": "image", "name": "Imagen", "extensions": [".png", ".jpg", ".jpeg", ".tiff"], "icon": "image"}
  ],
  "output_formats": [
    {"id": "markdown", "name": "Markdown", "extension": ".md", "mime_type": "text/markdown"},
    {"id": "html", "name": "HTML", "extension": ".html", "mime_type": "text/html"},
    {"id": "json", "name": "JSON", "extension": ".json", "mime_type": "application/json"}
  ]
}
```

---

## Configuración OCR

### Obtener Configuración OCR

```http
GET /api/settings/ocr
```

### Actualizar Configuración OCR

```http
PUT /api/settings/ocr
Content-Type: application/json
```

**Parámetros de Consulta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `auto_install` | boolean | Si es `true`, instala automáticamente los backends instalables mediante pip |

### Respuesta/Solicitud

```json
{
  "ocr": {
    "enabled": true,
    "language": "en",
    "force_full_page_ocr": false,
    "backend": "easyocr",
    "use_gpu": false,
    "confidence_threshold": 0.5,
    "bitmap_area_threshold": 0.05
  },
  "available_languages": [
    {"code": "en", "name": "Inglés"},
    {"code": "de", "name": "Alemán"},
    {"code": "fr", "name": "Francés"}
  ],
  "available_backends": [
    {"id": "easyocr", "name": "EasyOCR", "description": "OCR de propósito general con soporte GPU"},
    {"id": "tesseract", "name": "Tesseract", "description": "Motor OCR clásico"},
    {"id": "ocrmac", "name": "macOS Vision", "description": "OCR nativo de macOS (solo Mac)"},
    {"id": "rapidocr", "name": "RapidOCR", "description": "OCR rápido con runtime ONNX"}
  ]
}
```

---

## Gestión de Backends OCR

### Obtener Estado de Todos los Backends

```http
GET /api/settings/ocr/backends
```

Devuelve el estado de instalación de todos los backends OCR.

### Respuesta

```json
{
  "backends": [
    {
      "id": "easyocr",
      "name": "EasyOCR",
      "description": "OCR de propósito general con soporte GPU",
      "installed": true,
      "available": true,
      "error": null,
      "pip_installable": true,
      "requires_system_install": false,
      "platform": null,
      "note": "La primera ejecución descargará modelos de idioma (~100MB por idioma)"
    },
    {
      "id": "tesseract",
      "name": "Tesseract",
      "description": "Motor OCR clásico",
      "installed": false,
      "available": false,
      "error": "Paquete no instalado",
      "pip_installable": true,
      "requires_system_install": true,
      "platform": null,
      "note": "Requiere que Tesseract esté instalado en su sistema"
    }
  ],
  "current_platform": "darwin"
}
```

### Verificar Backend Específico

```http
GET /api/settings/ocr/backends/{backend_id}/check
```

### Respuesta

```json
{
  "backend": "easyocr",
  "installed": true,
  "available": true,
  "error": null,
  "pip_installable": true,
  "requires_system_install": false,
  "note": "La primera ejecución descargará modelos de idioma"
}
```

### Instalar Backend

```http
POST /api/settings/ocr/backends/{backend_id}/install
```

Instala un backend OCR instalable mediante pip.

### Respuesta (Éxito)

```json
{
  "message": "EasyOCR instalado correctamente",
  "success": true,
  "installed": true,
  "available": true,
  "note": "La primera ejecución descargará modelos de idioma"
}
```

### Respuesta (Ya Instalado)

```json
{
  "message": "easyocr ya está instalado y disponible",
  "already_installed": true
}
```

### Respuesta (Requiere Instalación del Sistema)

```json
{
  "message": "Error al instalar tesseract",
  "success": false,
  "error": "tesseract requiere instalación a nivel del sistema",
  "requires_system_install": true
}
```

---

## Configuración de Tablas

### Obtener Configuración de Tablas

```http
GET /api/settings/tables
```

### Actualizar Configuración de Tablas

```http
PUT /api/settings/tables
Content-Type: application/json
```

### Solicitud/Respuesta

```json
{
  "tables": {
    "enabled": true,
    "structure_extraction": true,
    "mode": "accurate",
    "do_cell_matching": true
  }
}
```

---

## Configuración de Imágenes

### Obtener Configuración de Imágenes

```http
GET /api/settings/images
```

### Actualizar Configuración de Imágenes

```http
PUT /api/settings/images
Content-Type: application/json
```

### Solicitud/Respuesta

```json
{
  "images": {
    "extract": true,
    "classify": true,
    "generate_page_images": false,
    "generate_picture_images": true,
    "generate_table_images": true,
    "images_scale": 1.0
  }
}
```

---

## Configuración de Enriquecimiento

### Obtener Configuración de Enriquecimiento

```http
GET /api/settings/enrichment
```

### Respuesta

```json
{
  "enrichment": {
    "code_enrichment": false,
    "formula_enrichment": false,
    "picture_classification": false,
    "picture_description": false
  },
  "options": {
    "code_enrichment": {
      "description": "Mejorar bloques de código con detección de idioma y resaltado de sintaxis",
      "default": false,
      "note": "Puede aumentar el tiempo de procesamiento"
    },
    "formula_enrichment": {
      "description": "Extraer representaciones LaTeX de fórmulas matemáticas",
      "default": false,
      "note": "Permite mejor renderizado de fórmulas en las exportaciones"
    },
    "picture_classification": {
      "description": "Clasificar imágenes por tipo (figura, gráfico, diagrama, foto, etc.)",
      "default": false,
      "note": "Añade etiquetas semánticas a las imágenes extraídas"
    },
    "picture_description": {
      "description": "Generar descripciones de imágenes usando modelos de visión IA",
      "default": false,
      "note": "Requiere descarga adicional de modelo, aumenta significativamente el tiempo de procesamiento"
    }
  }
}
```

### Actualizar Configuración de Enriquecimiento

```http
PUT /api/settings/enrichment
Content-Type: application/json
```

### Solicitud

```json
{
  "code_enrichment": true,
  "formula_enrichment": true
}
```

### Respuesta

```json
{
  "message": "Configuración de enriquecimiento actualizada",
  "enrichment": {
    "code_enrichment": true,
    "formula_enrichment": true,
    "picture_classification": false,
    "picture_description": false
  }
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code_enrichment` | boolean | Mejorar bloques de código con detección de idioma |
| `formula_enrichment` | boolean | Extraer LaTeX de fórmulas matemáticas |
| `picture_classification` | boolean | Clasificar imágenes por tipo semántico |
| `picture_description` | boolean | Generar subtítulos IA para imágenes |

!!! warning "Tiempo de Procesamiento"
    Habilitar `formula_enrichment` y especialmente `picture_description` puede aumentar significativamente el tiempo de procesamiento de documentos.

---

## Configuración de Rendimiento

### Obtener Configuración de Rendimiento

```http
GET /api/settings/performance
```

### Actualizar Configuración de Rendimiento

```http
PUT /api/settings/performance
Content-Type: application/json
```

### Solicitud/Respuesta

```json
{
  "performance": {
    "device": "auto",
    "num_threads": 4,
    "document_timeout": null
  }
}
```

---

## Configuración de Fragmentación

### Obtener Configuración de Fragmentación

```http
GET /api/settings/chunking
```

### Actualizar Configuración de Fragmentación

```http
PUT /api/settings/chunking
Content-Type: application/json
```

### Solicitud/Respuesta

```json
{
  "chunking": {
    "enabled": false,
    "max_tokens": 512,
    "merge_peers": true
  }
}
```

---

## Configuración de Salida

### Obtener Configuración de Salida

```http
GET /api/settings/output
```

### Actualizar Configuración de Salida

```http
PUT /api/settings/output
Content-Type: application/json
```

### Solicitud/Respuesta

```json
{
  "output": {
    "default_format": "markdown"
  }
}
```
