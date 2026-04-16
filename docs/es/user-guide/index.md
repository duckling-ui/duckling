# Guía del usuario

Cómo sacar partido a Duckling.

## Resumen

Duckling ofrece una interfaz completa para convertir documentos, con funciones avanzadas como OCR, extracción de tablas y fragmentación para RAG.

## Secciones

<div class="grid cards" markdown>

-   :material-star:{ .lg .middle } __Características__

    ---

    Panorama de lo que permite Duckling

    [:octicons-arrow-right-24: Características](features.md)

-   :material-file-document:{ .lg .middle } __Formatos compatibles__

    ---

    Referencia de formatos de entrada y salida

    [:octicons-arrow-right-24: Formatos](formats.md)

-   :material-cog:{ .lg .middle } __Configuración__

    ---

    Ajustar OCR, tablas, imágenes y rendimiento

    [:octicons-arrow-right-24: Configuración](configuration.md)

</div>

## Consejos rápidos

!!! tip "Varios archivos"
    Arrastra varios archivos, elige una carpeta o usa **Elegir archivos…** — la misma zona sirve para uno o muchos. La cola procesa hasta 2 conversiones en paralelo.

!!! tip "Elección de OCR"
    - **EasyOCR**: adecuado para documentos multilingües con GPU
    - **Tesseract**: fiable en documentos sencillos
    - **macOS Vision**: muy rápido en Mac con Apple Silicon
    - **RapidOCR**: ligero y rápido

!!! tip "Fragmentación RAG"
    Activa la fragmentación en la configuración para generar trozos de documento optimizados para RAG. Los fragmentos incluyen metadatos como encabezados y números de página.

