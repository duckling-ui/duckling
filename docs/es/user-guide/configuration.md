# Guía de configuración

Referencia completa de todas las opciones de configuración de Duckling.

## Variables de entorno

Cree un archivo `.env` en el directorio `backend`:

```env
# Flask Configuration
FLASK_ENV=development          # development | production | testing
SECRET_KEY=your-secret-key     # Required for production
DEBUG=True                     # Enable debug mode

# File Handling
MAX_CONTENT_LENGTH=104857600   # Max upload size in bytes (100MB default)

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///history.db
```

### Entorno de producción

```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key-here
DEBUG=False
MAX_CONTENT_LENGTH=209715200   # 200MB for production
```

!!! danger "Advertencia de seguridad"
    No use nunca la `SECRET_KEY` predeterminada en producción. Genere una clave aleatoria segura.

---

## Configuración OCR

El OCR (reconocimiento óptico de caracteres) extrae texto de imágenes y documentos escaneados.

### Opciones de configuración

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `enabled` | boolean | `true` | Activar o desactivar el OCR |
| `backend` | string | `"easyocr"` | Motor OCR a usar |
| `language` | string | `"en"` | Idioma principal de reconocimiento |
| `force_full_page_ocr` | boolean | `false` | OCR en toda la página frente a regiones detectadas |
| `use_gpu` | boolean | `false` | Aceleración por GPU (solo EasyOCR) |
| `confidence_threshold` | float | `0.5` | Confianza mínima de los resultados (0–1) |
| `bitmap_area_threshold` | float | `0.05` | Ratio mínimo de área para OCR de mapas de bits (0–1) |

### Motores OCR

=== "EasyOCR"

    Adecuado para documentos multilingües que requieren precisión.

    ```json
    {
      "ocr": {
        "backend": "easyocr",
        "use_gpu": true,
        "language": "en"
      }
    }
    ```

    - **GPU**: sí (CUDA)
    - **Idiomas**: más de 80
    - **Nota**: puede haber problemas de inicialización en algunos sistemas

=== "Tesseract"

    Motor OCR clásico y fiable para documentos simples.

    ```json
    {
      "ocr": {
        "backend": "tesseract",
        "language": "eng"
      }
    }
    ```

    - **GPU**: no
    - **Idiomas**: más de 100
    - **Requisito**: Tesseract instalado en el sistema

=== "macOS Vision"

    OCR nativo de macOS con el framework Vision de Apple.

    ```json
    {
      "ocr": {
        "backend": "ocrmac",
        "language": "en"
      }
    }
    ```

    - **GPU**: usa Apple Neural Engine
    - **Requisito**: macOS 10.15+
    - **Códigos de idioma**: Duckling acepta códigos cortos (`en`, `de`, `fr`, etc.) y los normaliza a etiquetas de localización Vision (p. ej. `en-US`) durante la conversión.

=== "RapidOCR"

    OCR rápido y ligero con ONNX Runtime.

    ```json
    {
      "ocr": {
        "backend": "rapidocr",
        "language": "en"
      }
    }
    ```

    - **GPU**: no
    - **Idiomas**: limitado

### Idiomas admitidos

| Código | Idioma | Código | Idioma |
|--------|--------|--------|--------|
| `en` | Inglés | `ja` | Japonés |
| `de` | Alemán | `zh` | Chino (simplificado) |
| `fr` | Francés | `zh-tw` | Chino (tradicional) |
| `es` | Español | `ko` | Coreano |
| `it` | Italiano | `ar` | Árabe |
| `pt` | Portugués | `hi` | Hindi |
| `nl` | Neerlandés | `th` | Tailandés |
| `pl` | Polaco | `vi` | Vietnamita |
| `ru` | Ruso | `tr` | Turco |

---

## Configuración de tablas

Configure cómo se detectan y extraen las tablas de los documentos.

### Opciones de configuración

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `enabled` | boolean | `true` | Activar detección de tablas |
| `structure_extraction` | boolean | `true` | Conservar la estructura de la tabla |
| `mode` | string | `"accurate"` | Modo de detección |
| `do_cell_matching` | boolean | `true` | Asociar el contenido de las celdas a la estructura |

### Modos de detección

=== "Modo preciso"

    ```json
    {
      "tables": {
        "enabled": true,
        "mode": "accurate",
        "do_cell_matching": true
      }
    }
    ```

    - Detección de tablas más precisa
    - Mejor reconocimiento de los límites de celda
    - Procesamiento más lento
    - Recomendado para tablas complejas

=== "Modo rápido"

    ```json
    {
      "tables": {
        "enabled": true,
        "mode": "fast",
        "do_cell_matching": false
      }
    }
    ```

    - Procesamiento más rápido
    - Adecuado para tablas simples
    - Puede omitir estructuras complejas

---

## Configuración de imágenes

Configure la extracción y el procesamiento de imágenes.

### Opciones de configuración

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `extract` | boolean | `true` | Extraer imágenes incrustadas |
| `classify` | boolean | `true` | Clasificar y etiquetar imágenes |
| `generate_page_images` | boolean | `false` | Crear una imagen por página |
| `generate_picture_images` | boolean | `true` | Extraer ilustraciones como archivos |
| `generate_table_images` | boolean | `true` | Extraer tablas como imágenes |
| `images_scale` | float | `1.0` | Factor de escala de imágenes (0,1 a 4,0) |

### Ejemplos de configuración

=== "Alta calidad"

    ```json
    {
      "images": {
        "extract": true,
        "classify": true,
        "generate_page_images": true,
        "generate_picture_images": true,
        "generate_table_images": true,
        "images_scale": 2.0
      }
    }
    ```

=== "Mínimo (solo texto)"

    ```json
    {
      "images": {
        "extract": false,
        "classify": false,
        "generate_page_images": false,
        "generate_picture_images": false,
        "generate_table_images": false
      }
    }
    ```

---

## Configuración de rendimiento

Optimice la velocidad de procesamiento y el uso de recursos.

### Opciones de configuración

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `device` | string | `"auto"` | Dispositivo de procesamiento |
| `num_threads` | int | `4` | Hilos de CPU (1–32) |
| `document_timeout` | int/null | `null` | Tiempo máximo de procesamiento en segundos |

### Opciones de dispositivo

| Dispositivo | Descripción | Ideal para |
|-------------|-------------|------------|
| `auto` | Selecciona automáticamente el mejor dispositivo | Uso general |
| `cpu` | Fuerza procesamiento en CPU | Servidores sin GPU |
| `cuda` | Aceleración GPU NVIDIA | Linux/Windows con GPU NVIDIA |
| `mps` | Apple Metal Performance Shaders | macOS con Apple Silicon |

### Ejemplos de configuración

=== "Alto rendimiento (GPU)"

    ```json
    {
      "performance": {
        "device": "cuda",
        "num_threads": 8,
        "document_timeout": null
      }
    }
    ```

=== "Recursos limitados"

    ```json
    {
      "performance": {
        "device": "cpu",
        "num_threads": 2,
        "document_timeout": 60
      }
    }
    ```

=== "Apple Silicon"

    ```json
    {
      "performance": {
        "device": "mps",
        "num_threads": 4,
        "document_timeout": null
      }
    }
    ```

---

## Configuración de fragmentación (chunking)

Configure el fragmentado de documentos para aplicaciones RAG.

### Opciones de configuración

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `enabled` | boolean | `false` | Activar fragmentación |
| `max_tokens` | int | `512` | Máximo de tokens por fragmento |
| `merge_peers` | boolean | `true` | Fusionar fragmentos demasiado pequeños |

### Ejemplos de configuración

=== "Optimizado para RAG"

    ```json
    {
      "chunking": {
        "enabled": true,
        "max_tokens": 512,
        "merge_peers": true
      }
    }
    ```

=== "Ventanas de contexto grandes"

    ```json
    {
      "chunking": {
        "enabled": true,
        "max_tokens": 2048,
        "merge_peers": false
      }
    }
    ```

---

## Configuración de salida

Defina el formato de salida predeterminado.

| Parámetro | Tipo | Predeterminado | Descripción |
|-----------|------|----------------|-------------|
| `default_format` | string | `"markdown"` | Formato de exportación predeterminado |

---

## Ejemplo de configuración completo

```json
{
  "ocr": {
    "enabled": true,
    "backend": "easyocr",
    "language": "en",
    "force_full_page_ocr": false,
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
  "performance": {
    "device": "auto",
    "num_threads": 4,
    "document_timeout": null
  },
  "chunking": {
    "enabled": false,
    "max_tokens": 512,
    "merge_peers": true
  },
  "output": {
    "default_format": "markdown"
  }
}
```

---

## Configuración vía API

### Obtener la configuración actual

```bash
curl http://localhost:5001/api/settings
```

### Actualizar la configuración

```bash
curl -X PUT http://localhost:5001/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "ocr": {"backend": "tesseract"},
    "performance": {"num_threads": 8}
  }'
```

### Restablecer valores predeterminados

```bash
curl -X POST http://localhost:5001/api/settings/reset
```

---

## Solución de problemas

### El OCR no funciona

1. **Error de inicialización de EasyOCR**: cambie a `ocrmac` (macOS) o `tesseract`
2. **Errores de GPU**: establezca `use_gpu: false`
3. **Resultados poco fiables**: baje `confidence_threshold`

### Procesamiento lento

1. Reduzca `images_scale` a `0.5`
2. Use `mode: "fast"` para tablas
3. Desactive `generate_page_images`
4. Aumente `num_threads`

### Problemas de memoria

1. Active `document_timeout` (p. ej. 120 segundos)
2. Procese menos archivos por lote
3. Reduzca `images_scale`
4. Desactive el chunking si no lo necesita
