# Docling docs

This section includes a **curated, vendored subset** of the upstream [Docling](https://github.com/docling-project/docling) documentation so Duckling users can quickly reference Docling concepts and usage without leaving this docs site.

!!! note "Upstream docs snapshot"
    The pages under **Docling docs** are derived from the upstream Docling project and are provided under the **MIT License** (same as Duckling). For the complete and most up-to-date documentation, see the official site: `https://docling-project.github.io/docling/`.

## Duckling and DocLang

Duckling can export converted documents to [DocLang](https://doclang.ai) (`.dclg.xml`) using Docling's `export_to_doclang()` API. DocLang is the open, AI-native document interchange format from the LF AI & Data DocLang working group. See [Supported formats](../user-guide/formats.md#doclang-dclgxml) in the Duckling user guide.

## Included pages

- [Installation](installation.md)
- [Quickstart](quickstart.md)
- [Supported formats](supported-formats.md)
- [Advanced options](advanced-options.md)
- [Architecture](architecture.md)
- [DoclingDocument](docling-document.md)

## Updating these pages

These files are intended to be refreshed from upstream using:

```bash
python3 scripts/sync_docling_docs.py
```

