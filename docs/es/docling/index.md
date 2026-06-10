# Documentación de Docling

Esta sección incluye una **selección** de la documentación oficial de Docling (en inglés) dentro de la documentación de Duckling.

!!! note "Contenido en inglés"
    Estas páginas se sincronizan desde el proyecto upstream `docling-project/docling` (MIT). Para la documentación completa y más reciente, consulta `https://docling-project.github.io/docling/`.

## Duckling y DocLang

Duckling puede exportar documentos convertidos a [DocLang](https://doclang.ai) (`.dclg.xml`) mediante la API `export_to_doclang()` de Docling. DocLang es el formato de intercambio de documentos nativo para IA del grupo de trabajo LF AI & Data DocLang. Vea [Formatos compatibles](../user-guide/formats.md#doclang-dclgxml) en la guía de usuario de Duckling.

## Páginas incluidas

- [Installation](installation.md)
- [Quickstart](quickstart.md)
- [Supported formats](supported-formats.md)
- [Advanced options](advanced-options.md)
- [Architecture](architecture.md)
- [DoclingDocument](docling-document.md)

## Actualizar estas páginas

Para volver a sincronizar desde el proyecto upstream:

```bash
python3 scripts/sync_docling_docs.py
```

