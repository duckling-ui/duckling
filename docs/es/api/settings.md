# API de configuración

Endpoints para gestionar la configuración de conversión.

!!! note "Almacenamiento basado en sesión"
    La configuración se almacena por sesión de usuario en la base de datos. La configuración de cada usuario está aislada y no afecta a otros usuarios, lo que hace que Duckling sea seguro en despliegues multiusuario.

## Obtener toda la configuración

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

## Actualizar configuración

```http
PUT /api/settings
Content-Type: application/json
```

### Cuerpo de la solicitud

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

## Restablecer la configuración a los valores predeterminados

```http
POST /api/settings/reset
```

### Respuesta

Devuelve el objeto de configuración predeterminado.

---

## Obtener formatos admitidos

```http
GET /api/settings/formats
```

### Respuesta

```json
{
  "input_formats": [
    {"id": "pdf", "name": "PDF Document", "extensions": [".pdf"], "icon": "document"},
    {"id": "docx", "name": "Microsoft Word", "extensions": [".docx"], "icon": "document"},
    {"id": "image", "name": "Image", "extensions": [".png", ".jpg", ".jpeg", ".tiff"], "icon": "image"}
  ],
  "output_formats": [
    {"id": "markdown", "name": "Markdown", "extension": ".md", "mime_type": "text/markdown"},
    {"id": "html", "name": "HTML", "extension": ".html", "mime_type": "text/html"},
    {"id": "json", "name": "JSON", "extension": ".json", "mime_type": "application/json"}
  ]
}
```

---

## Configuración de OCR

### Obtener la configuración de OCR

```http
GET /api/settings/ocr
```

### Actualizar la configuración de OCR

```http
PUT /api/settings/ocr
Content-Type: application/json
```

**Parámetros de consulta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `auto_install` | boolean | Si es `true`, instala automáticamente los backends instalables con pip |

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
    {"code": "en", "name": "English"},
    {"code": "de", "name": "German"},
    {"code": "fr", "name": "French"}
  ],
  "available_backends": [
    {"id": "easyocr", "name": "EasyOCR", "description": "General-purpose OCR with GPU support"},
    {"id": "tesseract", "name": "Tesseract", "description": "Classic OCR engine"},
    {"id": "ocrmac", "name": "macOS Vision", "description": "Native macOS OCR (Mac only)"},
    {"id": "rapidocr", "name": "RapidOCR", "description": "Fast OCR with ONNX runtime"}
  ]
}
```

---

## Gestión de backends de OCR

### Obtener el estado de todos los backends

```http
GET /api/settings/ocr/backends
```

Devuelve el estado de instalación de todos los backends de OCR.

### Respuesta

```json
{
  "backends": [
    {
      "id": "easyocr",
      "name": "EasyOCR",
      "description": "General-purpose OCR with GPU support",
      "installed": true,
      "available": true,
      "error": null,
      "pip_installable": true,
      "requires_system_install": false,
      "platform": null,
      "note": "First run will download language models (~100MB per language)"
    },
    {
      "id": "tesseract",
      "name": "Tesseract",
      "description": "Classic OCR engine",
      "installed": false,
      "available": false,
      "error": "Package not installed",
      "pip_installable": true,
      "requires_system_install": true,
      "platform": null,
      "note": "Requires Tesseract to be installed on your system"
    }
  ],
  "current_platform": "darwin"
}
```

### Comprobar un backend concreto

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
  "note": "First run will download language models"
}
```

### Instalar backend

```http
POST /api/settings/ocr/backends/{backend_id}/install
```

Instala un backend de OCR instalable con pip.

### Respuesta (correcto)

```json
{
  "message": "Successfully installed easyocr",
  "success": true,
  "installed": true,
  "available": true,
  "note": "First run will download language models"
}
```

### Respuesta (ya instalado)

```json
{
  "message": "easyocr is already installed and available",
  "already_installed": true
}
```

### Respuesta (requiere instalación del sistema)

```json
{
  "message": "Failed to install tesseract",
  "success": false,
  "error": "tesseract requires system-level installation",
  "requires_system_install": true
}
```

---

## Configuración de tablas

### Obtener la configuración de tablas

```http
GET /api/settings/tables
```

### Actualizar la configuración de tablas

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

## Configuración de imágenes

### Obtener la configuración de imágenes

```http
GET /api/settings/images
```

### Actualizar la configuración de imágenes

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

## Configuración de enriquecimiento

### Obtener la configuración de enriquecimiento

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
      "description": "Mejora los bloques de código con detección de idioma y resaltado de sintaxis",
      "default": false,
      "note": "Puede aumentar el tiempo de procesamiento"
    },
    "formula_enrichment": {
      "description": "Extrae representaciones LaTeX de fórmulas matemáticas",
      "default": false,
      "note": "Permite un mejor renderizado de fórmulas en las exportaciones"
    },
    "picture_classification": {
      "description": "Clasifica las imágenes por tipo (figura, gráfico, diagrama, foto, etc.)",
      "default": false,
      "note": "Añade etiquetas semánticas a las imágenes extraídas"
    },
    "picture_description": {
      "description": "Genera descripciones para imágenes usando modelos de visión con IA",
      "default": false,
      "note": "Requiere descargar modelos adicionales y aumenta notablemente el tiempo de procesamiento"
    }
  }
}
```

### Actualizar la configuración de enriquecimiento

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
  "message": "Enrichment settings updated",
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
| `code_enrichment` | boolean | Mejora los bloques de código con detección de idioma |
| `formula_enrichment` | boolean | Extrae LaTeX de fórmulas matemáticas |
| `picture_classification` | boolean | Clasifica las imágenes por tipo semántico |
| `picture_description` | boolean | Genera descripciones con IA para las imágenes |

!!! warning "Tiempo de procesamiento"
    Activar `formula_enrichment` y sobre todo `picture_description` puede aumentar de forma notable el tiempo de procesamiento de los documentos.

---

## Configuración de rendimiento

### Obtener la configuración de rendimiento

```http
GET /api/settings/performance
```

### Actualizar la configuración de rendimiento

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

## Configuración de fragmentación

### Obtener la configuración de fragmentación

```http
GET /api/settings/chunking
```

### Actualizar la configuración de fragmentación

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

## Configuración de salida

### Obtener la configuración de salida

```http
GET /api/settings/output
```

### Actualizar la configuración de salida

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

