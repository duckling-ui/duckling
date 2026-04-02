# Screenshots Gallery

This page provides a visual tour of the Duckling interface. All screenshots are captured in dark mode.

!!! note "Screenshot Status"
    Some screenshots may show placeholders. See the [Screenshot Guide](../assets/screenshots/SCREENSHOT_GUIDE.md) for capturing instructions.

## Main Interface

### Dropzone

The main upload area where you drag und drop documents for conversion.

=== "Empty State"

    <figure markdown="span">
      ![Dropzone Empty](../assets/screenshots/ui/dropzone-empty.png){ loading=lazy }
      <figcaption>Ready to receive files</figcaption>
    </figure>

=== "Drag Hover"

    <figure markdown="span">
      ![Dropzone Hover](../assets/screenshots/ui/dropzone-hover.svg){ loading=lazy }
      <figcaption>Visual feedback when dragging files</figcaption>
    </figure>

=== "Uploading"

    <figure markdown="span">
      ![Dropzone Uploading](../assets/screenshots/ui/dropzone-uploading.svg){ loading=lazy }
      <figcaption>Fortschrittsanzeige beim Hochladen</figcaption>
    </figure>

=== "Mehrere Dateien"

    <figure markdown="span">
      ![Mehrere Dateien](../assets/screenshots/ui/dropzone-batch.png){ loading=lazy }
      <figcaption>Mehrere Dateien zum Upload ausgewählt</figcaption>
    </figure>

### Header

<figure markdown="span">
  ![Header](../assets/screenshots/ui/header.png){ loading=lazy }
  <figcaption>Kopfzeile mit Einstellungen und Sprachwahl</figcaption>
</figure>

### History Panel

=== "History List"

    <figure markdown="span">
      ![History Panel](../assets/screenshots/ui/history-panel.png){ loading=lazy }
      <figcaption>List of previous conversions</figcaption>
    </figure>

=== "Search"

    <figure markdown="span">
      ![History Search](../assets/screenshots/ui/history-search.png){ loading=lazy }
      <figcaption>Searching conversion history</figcaption>
    </figure>

---

## Einstellungen Panel

### OCR-Einstellungen

=== "Übersicht"

    <figure markdown="span">
      ![OCR-Einstellungen](../assets/screenshots/settings/settings-ocr.png){ loading=lazy }
      <figcaption>OCR configuration options</figcaption>
    </figure>

=== "Install Backend"

    <figure markdown="span">
      ![OCR Install](../assets/screenshots/settings/settings-ocr-install.svg){ loading=lazy }
      <figcaption>One-click backend installation</figcaption>
    </figure>

=== "Tesseract Notice"

    <figure markdown="span">
      ![Tesseract](../assets/screenshots/settings/settings-ocr-tesseract.png){ loading=lazy }
      <figcaption>Manual installation instructions for Tesseract</figcaption>
    </figure>

### Tabelleneinstellungen

<figure markdown="span">
  ![Tabelleneinstellungen](../assets/screenshots/settings/settings-tables.svg){ loading=lazy }
  <figcaption>Table extraction configuration</figcaption>
</figure>

### Bildeinstellungen

<figure markdown="span">
  ![Bildeinstellungen](../assets/screenshots/settings/settings-images.svg){ loading=lazy }
  <figcaption>Image extraction options</figcaption>
</figure>

### Enrichment Einstellungen

=== "All Options"

    <figure markdown="span">
      ![Enrichment Einstellungen](../assets/screenshots/settings/settings-enrichment.png){ loading=lazy }
      <figcaption>Document enrichment options: code, formula, picture classification, und description</figcaption>
    </figure>

=== "Warning Message"

    <figure markdown="span">
      ![Enrichment Warning](../assets/screenshots/settings/settings-enrichment-warning.png){ loading=lazy }
      <figcaption>Warning displayed when slow enrichment features are enabled</figcaption>
    </figure>

### Leistung Einstellungen

<figure markdown="span">
  ![Leistung Einstellungen](../assets/screenshots/settings/settings-performance.svg){ loading=lazy }
  <figcaption>Verarbeitung performance configuration</figcaption>
</figure>

### Chunking Einstellungen

<figure markdown="span">
  ![Chunking Einstellungen](../assets/screenshots/settings/settings-chunking.svg){ loading=lazy }
  <figcaption>RAG chunking configuration</figcaption>
</figure>

### Output Einstellungen

<figure markdown="span">
  ![Output Einstellungen](../assets/screenshots/settings/settings-output.svg){ loading=lazy }
  <figcaption>Stundard output format selection</figcaption>
</figure>

---

## Export Options

### Format Selection

=== "All Formate"

    <figure markdown="span">
      ![Export Formate](../assets/screenshots/export/export-formats.png){ loading=lazy }
      <figcaption>Available export formats</figcaption>
    </figure>

=== "Selected Format"

    <figure markdown="span">
      ![Format Selected](../assets/screenshots/export/export-format-selected.png){ loading=lazy }
      <figcaption>Format selected with checkmark</figcaption>
    </figure>

### Preview Moduss

=== "Rendered/Raw Aktivieren"

    <figure markdown="span">
      ![Preview Aktivieren](../assets/screenshots/export/preview-toggle.png){ loading=lazy }
      <figcaption>Aktivieren between rendered und raw views</figcaption>
    </figure>

=== "Markdown Rendered"

    <figure markdown="span">
      ![Markdown Rendered](../assets/screenshots/export/preview-markdown-rendered.png){ loading=lazy }
      <figcaption>Rendered markdown with formatting</figcaption>
    </figure>

=== "Markdown Raw"

    <figure markdown="span">
      ![Markdown Raw](../assets/screenshots/export/preview-markdown-raw.png){ loading=lazy }
      <figcaption>Raw markdown source</figcaption>
    </figure>

=== "HTML Rendered"

    <figure markdown="span">
      ![HTML Rendered](../assets/screenshots/export/preview-html-rendered.png){ loading=lazy }
      <figcaption>Rendered HTML with styling</figcaption>
    </figure>

=== "HTML Raw"

    <figure markdown="span">
      ![HTML Raw](../assets/screenshots/export/preview-html-raw.png){ loading=lazy }
      <figcaption>Raw HTML source code</figcaption>
    </figure>

=== "JSON"

    <figure markdown="span">
      ![JSON Preview](../assets/screenshots/export/preview-json.png){ loading=lazy }
      <figcaption>Pretty-printed JSON output</figcaption>
    </figure>

---

## Funktionen in Action

### Konvertierung Status

=== "In Progress"

    <figure markdown="span">
      ![Konvertierung Progress](../assets/screenshots/features/conversion-progress.svg){ loading=lazy }
      <figcaption>Document being processed</figcaption>
    </figure>

=== "Complete"

    <figure markdown="span">
      ![Konvertierung Complete](../assets/screenshots/features/conversion-complete.svg){ loading=lazy }
      <figcaption>Successful conversion with stats</figcaption>
    </figure>

=== "Confidence Score"

    <figure markdown="span">
      ![Confidence Display](../assets/screenshots/features/confidence-display.svg){ loading=lazy }
      <figcaption>OCR confidence percentage</figcaption>
    </figure>

### Image Gallery

=== "Thumbnail Grid"

    <figure markdown="span">
      ![Images Gallery](../assets/screenshots/features/images-gallery.png){ loading=lazy }
      <figcaption>Extrahierened images as thumbnails</figcaption>
    </figure>

=== "Hover Actions"

    <figure markdown="span">
      ![Images Hover](../assets/screenshots/features/images-hover.png){ loading=lazy }
      <figcaption>View und download buttons on hover</figcaption>
    </figure>

=== "Lightbox"

    <figure markdown="span">
      ![Images Lightbox](../assets/screenshots/features/images-lightbox.png){ loading=lazy }
      <figcaption>Full-size image viewer with navigation</figcaption>
    </figure>

### Tables

=== "Table List"

    <figure markdown="span">
      ![Tables List](../assets/screenshots/features/tables-list.svg){ loading=lazy }
      <figcaption>Extrahierened tables with previews</figcaption>
    </figure>

=== "Herunterladen Options"

    <figure markdown="span">
      ![Tables Herunterladen](../assets/screenshots/features/tables-download.svg){ loading=lazy }
      <figcaption>CSV und image export options</figcaption>
    </figure>

### RAG Chunks

<figure markdown="span">
  ![Chunks List](../assets/screenshots/features/chunks-list.png){ loading=lazy }
  <figcaption>Document chunks with metadata</figcaption>
</figure>

