# Guide d'utilisation

Utilisez Duckling efficacement.

## Vue d'ensemble

Duckling offre une interface complète pour la conversion de documents, avec notamment l’OCR, l’extraction de tableaux et le découpage pour la RAG.

## Sections

<div class="grid cards" markdown>

-   :material-star:{ .lg .middle } __Fonctionnalités__

    ---

    Tour d’horizon des possibilités de Duckling

    [:octicons-arrow-right-24: Fonctionnalités](features.md)

-   :material-file-document:{ .lg .middle } __Formats pris en charge__

    ---

    Formats d’entrée et de sortie

    [:octicons-arrow-right-24: Formats](formats.md)

-   :material-cog:{ .lg .middle } __Configuration__

    ---

    Ajuster l’OCR, les tableaux, les images et les performances

    [:octicons-arrow-right-24: Configuration](configuration.md)

</div>

## Conseils rapides

!!! tip "Plusieurs fichiers"
    Glissez plusieurs fichiers, choisissez un dossier ou utilisez **Choisir des fichiers…** — la même zone gère un seul fichier ou plusieurs. La file traite jusqu’à 2 conversions en parallèle.

!!! tip "Choix de l’OCR"
    - **EasyOCR** : adapté aux documents multilingues avec accélération GPU
    - **Tesseract** : fiable pour les documents simples
    - **macOS Vision** : très rapide sur Mac avec Apple Silicon
    - **RapidOCR** : léger et rapide

!!! tip "Découpage RAG"
    Activez le découpage dans les paramètres pour produire des segments adaptés à la génération augmentée par récupération (RAG). Les segments incluent des métadonnées (titres, numéros de page).

