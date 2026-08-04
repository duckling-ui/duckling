# Docling-Dokumentation

Dieser Abschnitt enthält eine **kuratierte Auswahl** der offiziellen Docling-Dokumentation (auf Englisch) innerhalb der Duckling-Dokumentation.

!!! note "Inhalt auf Englisch"
    Diese Seiten werden aus dem Upstream-Projekt `docling-project/docling` (MIT) synchronisiert. Die vollständige und aktuellste Dokumentation findest du unter `https://docling-project.github.io/docling/`.

## Duckling und DocLang

Duckling kann konvertierte Dokumente als [DocLang](https://doclang.ai) (`.dclg.xml`) über Doclings `export_to_doclang()`-API exportieren. DocLang ist das offene, KI-native Austauschformat der LF AI & Data DocLang-Arbeitsgruppe. Siehe [Unterstützte Formate](../user-guide/formats.md#doclang-dclgxml) im Duckling-Benutzerhandbuch.

## Enthaltene Seiten

- [Installation](installation.md)
- [Quickstart](quickstart.md)
- [Supported formats](supported-formats.md)
- [Advanced options](advanced-options.md)
- [Architecture](architecture.md)
- [DoclingDocument](docling-document.md)

## Seiten aktualisieren

Diese Dateien können aus dem Upstream mit folgendem Befehl aktualisiert werden:

```bash
python3 scripts/sync_docling_docs.py
```

