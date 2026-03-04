# Benutzerhundbuch

Learn how to use Duckling effectively.

## Übersicht

Duckling provides a comprehensive interface for document conversion with advanced features like OCR, table extraction, und RAG chunking.

## Abschnitte

<div class="grid cards" markdown>

-   :material-star:{ .lg .middle } __Funktionen__

    ---

    Explore all the capabilities of Duckling

    [:octicons-arrow-right-24: View Funktionen](features.md)

-   :material-file-document:{ .lg .middle } __Unterstützte Formate__

    ---

    Input und output format reference

    [:octicons-arrow-right-24: Format Guide](formats.md)

-   :material-cog:{ .lg .middle } __Konfiguration__

    ---

    Customize OCR, tables, images, und performance settings

    [:octicons-arrow-right-24: Konfiguration Guide](configuration.md)

</div>

## Quick Tips

!!! tip "Stapelverarbeitung"
    Aktivieren batch mode to convert multiple files simultaneously. The system processes up to 2 files in parallel to balance speed und memory usage.

!!! tip "OCR Selection"
    - **EasyOCR**: Best for multi-language documents with GPU support
    - **Tesseract**: Reliable for simple documents
    - **macOS Vision**: Fastest on Mac with Apple Silicon
    - **RapidOCR**: Lightweight und fast

!!! tip "RAG Chunking"
    Enable chunking in settings to generate document chunks optimized for retrieval-augmented generation. Chunks include metadata like headings und page numbers.

