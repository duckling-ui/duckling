# Registro de cambios

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto se adhiere al [Versionado Semántico](https://semver.org/spec/v2.0.0.html).

**Última versión:** [0.0.11](https://github.com/duckling-ui/duckling/releases/tag/v0.0.11) (2026-03-30)

## [Sin publicar]

### Documentación

- **Despliegue**: [deployment/index.md](deployment/index.md), [deployment/production.md](deployment/production.md), [deployment/scaling.md](deployment/scaling.md) y [deployment/security.md](deployment/security.md) traducidos por completo (etiquetas Mermaid localizadas); equivalentes en `de`/`fr`.
- **Primeros pasos**: [index.md](getting-started/index.md), [installation.md](getting-started/installation.md), [quickstart.md](getting-started/quickstart.md) y [docker.md](getting-started/docker.md) traducidos por completo; reflejados en `de`/`fr`; redacción CI/CD aclarada en inglés [docker.md](../getting-started/docker.md).
- **Guía de usuario**: páginas [Formatos admitidos](user-guide/formats.md) y [Galería de capturas](user-guide/screenshots.md) traducidas por completo; equivalentes en `de`/`fr`.
- **Inicio rápido**: la sección « Varios archivos a la vez » en [getting-started/quickstart.md](getting-started/quickstart.md) documenta arrastrar una carpeta, clic en la zona para elegir carpeta y **Elegir archivos…** para varios archivos sueltos; reflejado en `de`/`fr`.
- **Francés / inglés**: `fr/user-guide/features.md` está traducida por completo (encabezados para la TOC lateral); se eliminó la subsección duplicada «Statistics Panel» en la página en inglés [user-guide/features.md](../user-guide/features.md).
- **Página de inicio**: [index.md](index.md) enlaza los anclajes en español de Características y añade enlace a [changelog.md](changelog.md); la portada en francés incluye lista de documentación y agradecimientos; la alemana enlaza Docling como en inglés.
- **Guía de usuario**: [Características](user-guide/features.md) y [Configuración](user-guide/configuration.md) traducidas por completo; mismas páginas en `de`/`fr`.
- **API**: [api/index.md](api/index.md), [api/conversion.md](api/conversion.md), [api/settings.md](api/settings.md) y [api/history.md](api/history.md) traducidos por completo; equivalentes en `de`/`fr`.
- **Arquitectura (páginas detalladas)**: [architecture/overview.md](architecture/overview.md), [architecture/components.md](architecture/components.md) y [architecture/diagrams.md](architecture/diagrams.md) traducidos por completo; equivalentes en `de`/`fr`.
- **Contribuir**: todas las páginas en [contributing/](contributing/index.md) traducidas; anclajes `{#commit-messages}` y `{#dco-sign-off}` en [contributing/code-style.md](contributing/code-style.md).
- **Docling / capturas**: sección de actualización en [docling/index.md](docling/index.md); [images/README.md](images/README.md) en español.

### Planificado

- Autenticación de usuarios
- Integración con almacenamiento en la nube
- Plantillas de conversión
- Limitación de tasa de API
- WebSocket para actualizaciones en tiempo real
- Alternancia tema oscuro/claro
- Atajos de teclado
- Mejoras de accesibilidad (WCAG 2.1)

## [0.0.11] - 2026-03-30

### Cambiado

- **UX de subida**: Se eliminó el interruptor de lote en la barra; una sola zona admite un archivo, varios, carpetas y URLs multilínea. Ver `CHANGELOG.md` en la raíz del repositorio para más detalles.
- **Dependencias**: Sin `requirements-docs.txt` en la raíz; usar solo **`backend/requirements.txt`** para MkDocs y la API (ver `CHANGELOG.md` en la raíz).

### Corregido

- **Pruebas del frontend**: La prueba de navegación por iframe de `DocsPanel` espera a que el listener de `message` se registre tras completar el `fetch` simulado y usa un `waitFor` más largo para que la CI sea estable en runners más lentos.
- **Docs / CI**: `pymdown-extensions>=10.21.2` evita un fallo de Pygments al construir el sitio (igual que `CHANGELOG.md` en la raíz).
- **Python / CI**: `markdown>=3.6` y `mkdocs>=1.6` en `backend/requirements.txt` para que pip resuelva el stack de documentación con pymdown 10.21.2+ (igual que `CHANGELOG.md` en la raíz).

## [0.0.10a] - 2026-03-23

### Corregido

- **Dependencias del backend**: Un solo archivo `backend/requirements.txt` para la API y las compilaciones MkDocs desde la UI; eliminado el duplicado `backend/requirements-docs.txt`.

### Cambios

- **Navegación de documentación**: Cambio de pestañas superiores horizontales a una barra lateral izquierda única con navegación de árbol colapsable; cada categoría principal (Inicio, Primeros pasos, etc.) se puede expandir o colapsar.
- **Mosaicos de características clave**: Cada mosaico de características en la página principal de la documentación es ahora un enlace clicable a su documentación detallada (página de Características o Formatos).
- **CONTRIBUTING.md**: Añadido requisito de firma DCO (Developer Certificate of Origin) para todos los commits.
- **Documentación de contribución**: Traducciones completas para alemán (de), español (es) y francés (fr); todas las localizaciones tienen ahora contenido consistente y completo incluyendo requisitos DCO.

### Seguridad

- Corregido path traversal de Rollup (GHSA-mw96-cpmx-2vgc) y ReDoS de Minimatch (GHSA-3ppc-4f35-3m26) mediante overrides de npm en frontend: `rollup >=4.59.0`, `minimatch 9.0.6` para `@typescript-eslint/typescript-estree`.
- Corregido Werkzeug safe_join con nombres de dispositivos Windows en rutas multi-segmento (CVE-2026-27199, GHSA-29vq-49wr-vm6x): actualizado werkzeug 3.1.4 → 3.1.6.
- Corregido encabezado Vary: Cookie de sesión Flask al usar operador `in` (CVE-2026-27205): actualizado flask 3.0.0 → 3.1.3.
- **Prevención SSRF**: Validación de URL antes de solicitudes salientes en `download_from_url`, `download_from_url_with_images` y `download_image`; bloquea loopback, IPs privadas, link-local, metadata y esquemas peligrosos.
- **Correcciones de seguridad CodeQL**:
  - SSRF: `validate_url_safe_for_request` ahora devuelve la URL validada; todas las llamadas `requests.get` usan el valor devuelto para satisfacer el análisis de flujo de datos.
  - ReDoS: Extracción de imágenes HTML limitada a 5MB antes del procesamiento regex para mitigar regex polinomial en contenido controlado por el usuario.
  - Path traversal: `delete_output_folder` ahora usa `validate_job_id` y `get_validated_output_dir` de utilidades de seguridad en lugar de comprobaciones manuales.
  - Exposición de información: Respuestas de error de la API de configuración sanitizadas mediante `_sanitize_error_for_client` para evitar fugas de stack trace o datos sensibles.

## [0.0.10a] - 2026-02-24

### Añadido

- **Flujo de publicación de imágenes Docker**: GitHub Action se ejecuta cuando los PR se fusionan en `main`, construyendo imágenes multi-plataforma y publicando en Docker Hub y GitHub Container Registry (requiere secretos `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN`).
- **Generar fragmentos ahora**: Botón en la pestaña Fragmentos RAG para generar fragmentos bajo demanda para documentos completados (`POST /api/history/{job_id}/generate-chunks`)
- **Deduplicación por contenido**: Mismo archivo + mismas configuraciones que afectan al documento reutilizan contenido almacenado en lugar de reconvertir
  - Acierto de caché: crear symlink, cargar metadatos, completar inmediatamente (sin ejecución Docling)
  - Fallo de caché: ejecutar conversión, mover salida al almacén de contenido, crear symlink
  - Migración de base de datos `scripts/migrate_add_content_hash.py` añade columna `content_hash`
- **Estadísticas y métricas de conversión**: Estadísticas de historial extendidas para análisis de uso de Docling y Duckling
  - `GET /api/history/stats` devuelve `avg_processing_seconds`, `ocr_backend_breakdown`, `output_format_breakdown`, `performance_device_breakdown`, `chunking_enabled_count`, `error_category_breakdown`, `source_type_breakdown` y `queue_depth`
  - Migración de base de datos `scripts/migrate_add_stats_columns.py` añade columnas de estadísticas a la tabla conversions
  - El panel de historial muestra tiempo medio de procesamiento y profundidad de cola cuando está disponible
- **Panel de estadísticas**: Visor dedicado para estadísticas de conversión (botón de cabecera, "Ver estadísticas completas" desde Historial)
- **Estadísticas extendidas**: Métricas de hardware y rendimiento en el panel de estadísticas
  - Sección sistema: tipo de hardware (CPU/CUDA/MPS), número de CPU, uso actual de CPU, información GPU
  - Páginas/segundo promedio y páginas/segundo por CPU
  - Distribución de tiempo de conversión (mediana, percentil 95, percentil 99)
  - Gráfico de páginas/segundo a lo largo del tiempo
  - Uso de CPU promediado durante cada conversión (almacenado en DB)
  - Migración de base de datos `scripts/migrate_add_cpu_usage_column.py` añade columna `cpu_usage_avg_during_conversion`
  - El uso de CPU es ahora específico del proceso (proceso backend Duckling, ejecuta Docling), no del sistema completo
  - Configuración por conversión almacenada: `performance_device_used` (resuelto de "auto" al completar), `images_classify_enabled`
  - Migración de base de datos `scripts/migrate_add_config_columns.py` añade estas columnas
  - Desglose de estadísticas por hardware, backend OCR, clasificador de imágenes (páginas/seg, tiempo de conversión por config)
- Soporte de idiomas de interfaz (Inglés `en`, Español `es`, Francés `fr`, Alemán `de`) con selector de idioma.
- Documentación MkDocs multilingüe (Inglés, Español, Francés, Alemán) servida bajo `/api/docs/site/<locale>/`.
- Etiquetas de categorías del panel Dropzone (Documentos, Web, Imágenes, Datos) ahora totalmente internacionalizadas.
- Sección de documentación Docling en MkDocs (subconjunto curado y vendido de documentación Docling upstream + script de sincronización).
- **Configuración de usuario por sesión**: Configuración de usuario almacenada por sesión en la base de datos en lugar de un archivo compartido.

### Seguridad

- Corregidas vulnerabilidades de seguridad del frontend (esbuild GHSA-67mh-4wv8-2f99): Actualizado Vite 5→7, Vitest 1→4 y dependencias relacionadas.

### Cambios

- Punto de entrada del backend renombrado de `app.py` a `duckling.py` para mayor claridad.
- Nombre de la aplicación Flask cambiado a "duckling" (se muestra como "Serving Flask app 'duckling'").

### Corregido

- La navegación de documentación ahora muestra nombres de páginas totalmente localizados en todos los idiomas soportados.
- Las etiquetas de categorías de formato de archivo del Dropzone ahora se traducen correctamente según el idioma seleccionado.
- Mejorada la extracción de títulos de páginas de documentación con mejor fallback a nombres traducidos.
- Los enlaces prev/siguiente del pie del panel de documentación integrada permanecen dentro de la categoría actual de la barra lateral, y navegar dentro de la documentación integrada mantiene la selección de la barra lateral sincronizada.
- Corregido fallo de reconstrucción de documentación integrada con `cannot access local variable 'shutil'` al construir el sitio MkDocs.
- La reconstrucción de documentación del backend ahora prefiere el entorno MkDocs `./venv` local del repositorio para asegurar que los plugins requeridos (como `i18n`) estén disponibles.
- Corregido que al hacer clic en una entrada del historial no se cargaba el documento; ahora usa el endpoint de carga del historial (disco) en lugar del endpoint de resultado en memoria.
- Cuando falta `document_json_path` en la DB, la carga del historial encuentra y carga `*.document.json` del directorio de salida para que se carguen todos los elementos del historial, no solo el primero.
- El panel de visualización de documentos ahora se actualiza al cargar un elemento diferente del historial (usa clave de componente para remontar con estado fresco).
- Actualizado `vitest.config.ts` para compatibilidad con Vitest 4.
- Actualizado requisito de versión Node.js de CI/CD a 22 (requerido para Vite 7).

## [0.0.9] - 2026-01-08

### Añadido

- **Personalización**: Logo de Duckling y visualización de versión en la cabecera.
- **Conversión de documentos por URL**: Convertir documentos desde URLs con extracción automática de imágenes para HTML.
- **Opciones de enriquecimiento de documentos**: Enriquecimiento de código, fórmulas, clasificación de imágenes, descripción de imágenes.
- **Descarga previa de modelos de enriquecimiento**: Descargar modelos de IA antes del procesamiento.
- **Galería de vista previa de imágenes**: Miniaturas visuales con visor lightbox.
- **Instalación automática de backends OCR**: Instalación con un clic para backends instalables por pip.
- **Vista previa específica por formato**: El panel de vista previa muestra el contenido en el formato de exportación seleccionado.
- **Modo vista previa renderizado vs crudo**: Alternancia para HTML y Markdown.
- **Soporte Docker mejorado**: Dockerfiles multi-etapa, variantes docker-compose, builds multi-plataforma.

### Corregido

- Recuperación de contenido multi-worker (imágenes, tablas, resultados).
- Vista previa HTML en la interfaz.
- Extracción de imágenes URL para atributos `src` sin comillas.
- El panel de documentación ahora sirve el sitio MkDocs preconstruido.
- Variables de entorno y carga de `.env`.
- Extensiones de archivo insensibles a mayúsculas.
- Puntuación de confianza y selección de backend OCR.

## [0.0.8] - 2026-01-07

### Cambios

- **Renombrado**: Proyecto renombrado de "Docling UI" a "Duckling"
  - Actualizada toda la documentación, código y archivos de configuración
  - Marca actualizada en toda la aplicación

## [0.0.7] - 2026-01-07

### Añadido

- **Documentación MkDocs**: Migración de documentación a MkDocs con tema Material
  - Sitio de documentación moderno y buscable
  - Alternancia tema oscuro/claro
  - Soporte de diagramas Mermaid
  - Navegación y organización mejoradas

### Cambios

- Estructura de documentación reorganizada para mejor navegación
- Todos los diagramas convertidos a formato Mermaid para renderizado en vivo

## [0.0.6] - 2025-12-11

### Seguridad

- **CRÍTICO**: Corregido modo debug de Flask habilitado por defecto en producción
  - El modo debug ahora se controla por la variable de entorno `FLASK_DEBUG` (por defecto: false)
  - El binding de host por defecto es `127.0.0.1` en lugar de `0.0.0.0`
- **ALTO**: Actualizadas dependencias vulnerables
  - `flask-cors`: 4.0.0 → 6.0.0 (CVE-2024-1681, CVE-2024-6844, CVE-2024-6866, CVE-2024-6839)
  - `gunicorn`: 21.2.0 → 23.0.0 (CVE-2024-1135, CVE-2024-6827)
  - `werkzeug`: 3.0.1 → 3.1.4 (CVE-2024-34069, CVE-2024-49766, CVE-2024-49767, CVE-2025-66221)
- **MEDIO**: Añadida protección contra path traversal en endpoints de servicio de archivos
  - El servicio de imágenes valida que las rutas no escapen de directorios permitidos
  - Bloquea secuencias de traversión de directorios (`..`)
- **MEDIO**: Mejorada sanitización de consultas SQL
  - Las consultas de búsqueda ahora escapan comodines LIKE
  - Añadidos límites de longitud de consulta
- Añadido `SECURITY.md` completo con:
  - Resumen de auditoría de seguridad
  - Lista de comprobación de despliegue en producción
  - Documentación de variables de entorno
  - Directrices de reporte de vulnerabilidades

### Cambios

- El backend ahora usa variables de entorno para toda la configuración sensible a seguridad
- Host por defecto cambiado de `0.0.0.0` a `127.0.0.1` para valores por defecto más seguros

## [0.0.5] - 2025-12-10

### Añadido

- **Procesamiento por lotes**: Subir y convertir múltiples archivos a la vez
  - Alternar modo lotes en la cabecera
  - Procesar múltiples documentos simultáneamente

- **Extracción de imágenes y tablas**:
  - Extraer imágenes incrustadas de documentos
  - Descargar imágenes individuales
  - Extraer tablas con preservación completa de datos
  - Exportar tablas a formato CSV
  - Ver vistas previas de tablas en la interfaz

- **Soporte RAG/Fragmentación**:
  - Fragmentación de documentos para aplicaciones RAG
  - Tokens máximos configurables por fragmento (64-8192)
  - Opción de fusionar fragmentos pequeños
  - Descargar fragmentos como JSON

- **Formatos de exportación adicionales**:
  - Tokens de documento (`.tokens.json`)
  - Fragmentos RAG (`.chunks.json`)
  - Exportación DocTags mejorada

- **Opciones OCR avanzadas**:
  - Múltiples backends OCR: EasyOCR, Tesseract, macOS Vision, RapidOCR
  - Soporte de aceleración GPU (EasyOCR)
  - Umbral de confianza configurable (0-1)
  - Control de umbral de área de bitmap
  - Soporte para más de 28 idiomas

- **Opciones de estructura de tablas**:
  - Modos de detección Rápido vs Preciso
  - Configuración de coincidencia de celdas
  - Alternancia de extracción de estructura

- **Opciones de generación de imágenes**:
  - Generar imágenes de página
  - Extraer imágenes de figuras
  - Extraer imágenes de tablas
  - Escala de imagen configurable (0.1x - 4.0x)

- **Opciones de rendimiento/acelerador**:
  - Selección de dispositivo: Auto, CPU, CUDA, MPS (Apple Silicon)
  - Configuración de número de hilos (1-32)
  - Configuración de timeout de documento

- **Nuevos endpoints API**:
  - `POST /api/convert/batch` - Conversión por lotes
  - `GET /api/convert/<job_id>/images` - Listar imágenes extraídas
  - `GET /api/convert/<job_id>/images/<id>` - Descargar imagen
  - `GET /api/convert/<job_id>/tables` - Listar tablas extraídas
  - `GET /api/convert/<job_id>/tables/<id>/csv` - Descargar CSV de tabla
  - `GET /api/convert/<job_id>/tables/<id>/image` - Descargar imagen de tabla
  - `GET /api/convert/<job_id>/chunks` - Obtener fragmentos de documento
  - `GET/PUT /api/settings/performance` - Configuración de rendimiento
  - `GET/PUT /api/settings/chunking` - Configuración de fragmentación
  - `GET /api/settings/formats` - Listar todos los formatos soportados

### Cambios

- **Panel de configuración**: Rediseñado completamente con todas las nuevas opciones
- **Opciones de exportación**: Mejoradas con pestañas para diferentes tipos de contenido
- **DropZone**: Actualizado con categorías de formato y soporte de modo lotes
- **Servicio de conversión**: Refactorización mayor para opciones de pipeline dinámicas

### Corregido

- El cálculo de puntuación de confianza ahora usa predicciones a nivel de cluster
- Mejor manejo del éxito parcial de conversión

## [0.0.4] - 2025-12-10

### Añadido

- **Soporte OCR**: Integración OCR completa usando EasyOCR
  - Soporte para más de 14 idiomas
  - Opción Forzar OCR de página completa
  - Configuración OCR configurable
- **Cálculo de confianza mejorado**: Confianza promedio de predicciones de layout

### Cambios

- Actualizado servicio de conversión para usar opciones de pipeline configurables
- Panel de configuración mejorado con opciones OCR

## [0.0.3] - 2025-12-10

### Añadido

- Lanzamiento inicial de Duckling
- **Características del frontend**:
  - Subida de archivos por arrastrar y soltar
  - Progreso de conversión en tiempo real
  - Opciones de exportación multi-formato
  - Panel de configuración
  - Panel de historial de conversiones
  - Tema oscuro con acento verde azulado
  - Diseño responsivo
  - Transiciones animadas

- **Características del backend**:
  - API REST Flask con CORS
  - Conversión de documentos asíncrona
  - Historial basado en SQLite
  - Gestión de subida de archivos
  - Configuración configurable
  - Endpoint de comprobación de salud

- **Formatos de entrada soportados**:
  - PDF, Word, PowerPoint, Excel
  - HTML, Markdown, CSV
  - Imágenes (PNG, JPG, TIFF, etc.)
  - AsciiDoc, XML

- **Formatos de exportación**:
  - Markdown, HTML, JSON
  - DocTags, texto plano

- **Experiencia de desarrollador**:
  - Suites de pruebas completas
  - Soporte Docker
  - TypeScript
  - Configuración ESLint

### Seguridad

- Validación de entrada para subida de archivos
- Restricciones de tipo de archivo
- Límites de tamaño máximo de archivo
- Manejo seguro de nombres de archivo

[Unreleased]: https://github.com/duckling-ui/duckling/compare/v0.0.11...HEAD
[0.0.11]: https://github.com/duckling-ui/duckling/compare/v0.0.10a...v0.0.11
[0.0.10a]: https://github.com/duckling-ui/duckling/compare/v0.0.10...v0.0.10a
[0.0.10]: https://github.com/duckling-ui/duckling/compare/v0.0.9...v0.0.10
[0.0.9]: https://github.com/duckling-ui/duckling/compare/v0.0.8...v0.0.9
[0.0.8]: https://github.com/duckling-ui/duckling/compare/v0.0.7...v0.0.8
[0.0.7]: https://github.com/duckling-ui/duckling/compare/v0.0.6...v0.0.7
[0.0.6]: https://github.com/duckling-ui/duckling/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/duckling-ui/duckling/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/duckling-ui/duckling/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/duckling-ui/duckling/releases/tag/v0.0.3
