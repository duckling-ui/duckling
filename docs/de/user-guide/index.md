# Benutzerhandbuch

So nutzen Sie Duckling effektiv.

## Übersicht

Duckling bietet eine umfassende Oberfläche zur Dokumentkonvertierung mit Funktionen wie OCR, Tabellenextraktion und RAG-Segmentierung.

## Abschnitte

<div class="grid cards" markdown>

-   :material-star:{ .lg .middle } __Funktionen__

    ---

    Alle Möglichkeiten von Duckling im Überblick

    [:octicons-arrow-right-24: Funktionen](features.md)

-   :material-file-document:{ .lg .middle } __Unterstützte Formate__

    ---

    Referenz zu Eingabe- und Ausgabeformaten

    [:octicons-arrow-right-24: Formate](formats.md)

-   :material-cog:{ .lg .middle } __Konfiguration__

    ---

    OCR, Tabellen, Bilder und Leistung anpassen

    [:octicons-arrow-right-24: Konfiguration](configuration.md)

</div>

## Kurze Tipps

!!! tip "Mehrere Dateien"
    Mehrere Dateien ziehen, Ordner wählen oder **Dateien wählen…**—dieselbe Zone für einzelne und Mehrfach-Uploads. Die Warteschlange verarbeitet bis zu 2 Konvertierungen parallel.

!!! tip "OCR-Auswahl"
    - **EasyOCR**: Gut für mehrsprachige Dokumente mit GPU-Unterstützung
    - **Tesseract**: Zuverlässig für einfache Dokumente
    - **macOS Vision**: Schnell auf dem Mac mit Apple Silicon
    - **RapidOCR**: Leichtgewichtig und schnell

!!! tip "RAG-Segmentierung"
    Aktivieren Sie die Segmentierung in den Einstellungen, um Dokumentabschnitte für Retrieval-Augmented Generation zu erzeugen. Die Segmente enthalten Metadaten wie Überschriften und Seitenzahlen.

!!! tip "DocLang-Export"
    Duckling kann [DocLang](https://doclang.ai) (`.dclg.xml`) exportieren — ein KI-natives XML-Format mit Struktur, Layout und Geometrie. Siehe [Unterstützte Formate — DocLang](formats.md#doclang-dclgxml). Erfordert Docling 2.70.0+; nach einem Dependency-Upgrade erneut konvertieren.

