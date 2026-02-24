# Funciones

Traducción en progreso.

## Historial de Conversiones

Accede a documentos previamente convertidos:

- Ver estado de conversión y metadatos
- Volver a descargar archivos convertidos
- Buscar en el historial por nombre de archivo
- Ver estadísticas de conversión

### Funcionalidades del Historial

- **Búsqueda**: Encontrar documentos por nombre de archivo
- **Filtro**: Filtrar por estado (completado, fallido)
- **Exportar**: Descargar historial como JSON
- **Recargar Documentos**: Haz clic en entradas del historial completadas para recargar el documento convertido sin re-conversión
  - Los documentos se almacenan automáticamente en disco después de la conversión
  - La estructura completa del documento se preserva y puede recargarse instantáneamente
- **Deduplicación de contenido**: El mismo archivo con configuraciones idénticas reutiliza la salida almacenada
- **Generar Chunks Ahora**: Cuando no existen chunks RAG, generarlos bajo demanda con la configuración de chunking actual (sin re-conversión)
  - Las conversiones con contenido de archivo y configuraciones que afectan al documento (OCR, tablas, imágenes) coincidentes se completan al instante desde la caché
  - Las salidas se almacenan una vez en un almacén direccionado por contenido y se comparten mediante enlaces simbólicos

### Panel de Estadísticas

Un panel deslizante dedicado para análisis completos de conversión. Ábrelo mediante el botón **Estadísticas** en el encabezado o el enlace **Ver estadísticas completas** en el panel Historial.

**Resumen:**

- Conversiones totales, conteos de éxito/fallo, tasa de éxito
- Tiempo de procesamiento promedio y profundidad de la cola

**Uso de almacenamiento:**

- Cargas, salidas y almacenamiento total

**Desgloses:**

- Formatos de entrada, backends OCR, formatos de salida
- Dispositivos de rendimiento (CPU/CUDA/MPS), tipos de origen
- Categorías de errores
- Conteo con chunking habilitado

**Métricas extendidas:**

- **Sistema**: Tipo de hardware (CPU/CUDA/MPS), número de CPU, uso actual de CPU (proceso backend Duckling), información GPU
- **Rendimiento**: Páginas/seg promedio y páginas/seg por CPU
- **Distribución del tiempo de conversión**: Mediana, percentiles 95 y 99
- **Páginas/seg en el tiempo**: Gráfico del rendimiento en el historial de conversiones
- **Rendimiento por configuración**: Páginas/seg y tiempo de conversión por hardware, backend OCR y clasificador de imágenes

