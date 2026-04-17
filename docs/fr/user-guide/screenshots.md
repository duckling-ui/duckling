# Galerie de captures d’écran

Cette page propose une visite visuelle de l’interface Duckling. Toutes les captures sont en mode sombre.

!!! note "État des captures"
    Certaines images peuvent afficher des espaces réservés. Consultez le [guide des captures d’écran](../../assets/screenshots/SCREENSHOT_GUIDE.md) pour les instructions de prise de vue.

## Interface principale

### Zone de dépôt

Zone principale où vous glissez-déposez les documents à convertir.

=== "État vide"

    <figure markdown="span">
      ![Zone de dépôt vide](../../assets/screenshots/ui/dropzone-empty.png){ loading=lazy }
      <figcaption>Prête à recevoir des fichiers</figcaption>
    </figure>

=== "Survol pendant le glisser-déposer"

    <figure markdown="span">
      ![Survol de la zone de dépôt](../../assets/screenshots/ui/dropzone-hover.svg){ loading=lazy }
      <figcaption>Retour visuel pendant le glissement des fichiers</figcaption>
    </figure>

=== "Téléversement"

    <figure markdown="span">
      ![Téléversement](../../assets/screenshots/ui/dropzone-uploading.svg){ loading=lazy }
      <figcaption>Indicateur de progression du téléversement</figcaption>
    </figure>

=== "Plusieurs fichiers"

    <figure markdown="span">
      ![Plusieurs fichiers](../../assets/screenshots/ui/dropzone-batch.png){ loading=lazy }
      <figcaption>Plusieurs fichiers sélectionnés pour le téléversement</figcaption>
    </figure>

### En-tête

<figure markdown="span">
  ![En-tête](../../assets/screenshots/ui/header.png){ loading=lazy }
  <figcaption>En-tête avec paramètres et choix de la langue</figcaption>
</figure>

### Panneau d’historique

=== "Liste d’historique"

    <figure markdown="span">
      ![Panneau d’historique](../../assets/screenshots/ui/history-panel.png){ loading=lazy }
      <figcaption>Liste des conversions précédentes</figcaption>
    </figure>

=== "Recherche"

    <figure markdown="span">
      ![Recherche dans l’historique](../../assets/screenshots/ui/history-search.png){ loading=lazy }
      <figcaption>Recherche dans l’historique des conversions</figcaption>
    </figure>

---

## Panneau des paramètres

### Paramètres OCR

=== "Vue d’ensemble"

    <figure markdown="span">
      ![Paramètres OCR](../../assets/screenshots/settings/settings-ocr-fr.png){ loading=lazy }
      <figcaption>Options de configuration OCR</figcaption>
    </figure>

=== "Installer le backend"

    <figure markdown="span">
      ![Installation OCR](../../assets/screenshots/settings/settings-ocr-install-fr.png){ loading=lazy }
      <figcaption>Installation du backend en un clic</figcaption>
    </figure>

=== "Avis Tesseract"

    <figure markdown="span">
      ![Tesseract](../../assets/screenshots/settings/settings-ocr-install-fr.png){ loading=lazy }
      <figcaption>Instructions d’installation manuelle de Tesseract</figcaption>
    </figure>

### Paramètres des tableaux

<figure markdown="span">
  ![Paramètres des tableaux](../../assets/screenshots/settings/settings-tables.svg){ loading=lazy }
  <figcaption>Configuration de l’extraction des tableaux</figcaption>
</figure>

### Paramètres des images

<figure markdown="span">
  ![Paramètres des images](../../assets/screenshots/settings/settings-images.svg){ loading=lazy }
  <figcaption>Options d’extraction des images</figcaption>
</figure>

### Paramètres d’enrichissement

=== "Toutes les options"

    <figure markdown="span">
      ![Paramètres d’enrichissement](../../assets/screenshots/settings/settings-enrichment.png){ loading=lazy }
      <figcaption>Enrichissement du document : code, formules, classification d’images et description</figcaption>
    </figure>

=== "Message d’avertissement"

    <figure markdown="span">
      ![Avertissement enrichissement](../../assets/screenshots/settings/settings-enrichment-warning.png){ loading=lazy }
      <figcaption>Avertissement lorsque des fonctions d’enrichissement lentes sont activées</figcaption>
    </figure>

### Paramètres de performance

<figure markdown="span">
  ![Paramètres de performance](../../assets/screenshots/settings/settings-performance.svg){ loading=lazy }
  <figcaption>Configuration des performances de traitement</figcaption>
</figure>

### Paramètres de découpage (chunking)

<figure markdown="span">
  ![Paramètres de chunking](../../assets/screenshots/settings/settings-chunking.svg){ loading=lazy }
  <figcaption>Configuration du découpage pour le RAG</figcaption>
</figure>

### Paramètres de sortie

<figure markdown="span">
  ![Paramètres de sortie](../../assets/screenshots/settings/settings-output.svg){ loading=lazy }
  <figcaption>Choix du format de sortie par défaut</figcaption>
</figure>

---

## Options d’export

### Choix du format

=== "Tous les formats"

    <figure markdown="span">
      ![Formats d’export](../../assets/screenshots/export/export-formats.png){ loading=lazy }
      <figcaption>Formats d’export disponibles</figcaption>
    </figure>

=== "Format sélectionné"

    <figure markdown="span">
      ![Format sélectionné](../../assets/screenshots/export/export-format-selected.png){ loading=lazy }
      <figcaption>Format sélectionné avec une coche</figcaption>
    </figure>

### Modes d’aperçu

=== "Basculer rendu / brut"

    <figure markdown="span">
      ![Bascule aperçu](../../assets/screenshots/export/preview-toggle.png){ loading=lazy }
      <figcaption>Basculer entre vue rendue et vue brute</figcaption>
    </figure>

=== "Markdown rendu"

    <figure markdown="span">
      ![Markdown rendu](../../assets/screenshots/export/preview-markdown-rendered.png){ loading=lazy }
      <figcaption>Markdown rendu avec mise en forme</figcaption>
    </figure>

=== "Markdown brut"

    <figure markdown="span">
      ![Markdown brut](../../assets/screenshots/export/preview-markdown-raw.png){ loading=lazy }
      <figcaption>Source Markdown brute</figcaption>
    </figure>

=== "HTML rendu"

    <figure markdown="span">
      ![HTML rendu](../../assets/screenshots/export/preview-html-rendered.png){ loading=lazy }
      <figcaption>HTML rendu avec styles</figcaption>
    </figure>

=== "HTML brut"

    <figure markdown="span">
      ![HTML brut](../../assets/screenshots/export/preview-html-raw.png){ loading=lazy }
      <figcaption>Code source HTML brut</figcaption>
    </figure>

=== "JSON"

    <figure markdown="span">
      ![Aperçu JSON](../../assets/screenshots/export/preview-json.png){ loading=lazy }
      <figcaption>Sortie JSON mise en forme</figcaption>
    </figure>

---

## Fonctionnalités en action

### État de la conversion

=== "En cours"

    <figure markdown="span">
      ![Conversion en cours](../../assets/screenshots/features/conversion-progress.svg){ loading=lazy }
      <figcaption>Document en cours de traitement</figcaption>
    </figure>

=== "Terminé"

    <figure markdown="span">
      ![Conversion terminée](../../assets/screenshots/features/conversion-complete-fr.png){ loading=lazy }
      <figcaption>Conversion réussie avec statistiques</figcaption>
    </figure>

=== "Score de confiance"

    <figure markdown="span">
      ![Affichage de la confiance](../../assets/screenshots/features/confidence-display.svg){ loading=lazy }
      <figcaption>Pourcentage de confiance OCR</figcaption>
    </figure>

### Galerie d’images

=== "Grille de miniatures"

    <figure markdown="span">
      ![Galerie d’images](../../assets/screenshots/features/images-gallery.png){ loading=lazy }
      <figcaption>Images extraites sous forme de miniatures</figcaption>
    </figure>

=== "Actions au survol"

    <figure markdown="span">
      ![Survol des images](../../assets/screenshots/features/images-hover.png){ loading=lazy }
      <figcaption>Boutons afficher et télécharger au survol</figcaption>
    </figure>

=== "Visionneuse plein écran"

    <figure markdown="span">
      ![Lightbox images](../../assets/screenshots/features/images-lightbox.png){ loading=lazy }
      <figcaption>Visionneuse en taille réelle avec navigation</figcaption>
    </figure>

### Tableaux

=== "Liste des tableaux"

    <figure markdown="span">
      ![Liste des tableaux](../../assets/screenshots/features/tables-list.svg){ loading=lazy }
      <figcaption>Tableaux extraits avec aperçus</figcaption>
    </figure>

=== "Options de téléchargement"

    <figure markdown="span">
      ![Téléchargement tableaux](../../assets/screenshots/features/tables-download.svg){ loading=lazy }
      <figcaption>Export CSV et image</figcaption>
    </figure>

### Fragments RAG

<figure markdown="span">
  ![Liste des fragments](../../assets/screenshots/features/chunks-list.png){ loading=lazy }
  <figcaption>Fragments de document avec métadonnées</figcaption>
</figure>
