# Duckling

Une interface Web moderne et conviviale pour [Docling](https://github.com/docling-project/docling) (IBM), la puissante bibliothèque de conversion de documents.

![Capture d'écran Duckling](fr/main-french.png)

## Aperçu

Duckling fournit une interface Web intuitive pour convertir des documents avec Docling. Que vous souhaitiez extraire du texte depuis des PDF, convertir des documents Word en Markdown ou effectuer de l’OCR sur des images numérisées, Duckling simplifie le tout.

## Fonctionnalités principales

<div class="grid cards" markdown>

-   <a href="user-guide/features/#glisser-deposer" class="card-link" markdown="1" aria-label="Guide utilisateur : section Téléversement par glisser-déposer">
    :material-cursor-move:{ .lg .middle } __Téléversement par glisser-déposer__

    ---

    Glissez simplement vos documents sur l'interface pour un traitement instantané
    </a>

-   <a href="user-guide/features/#plusieurs-fichiers-et-dossiers" class="card-link" markdown="1" aria-label="Guide utilisateur : section Traitement par lot">
    :material-file-multiple:{ .lg .middle } __Traitement par lot__

    ---

    Convertissez plusieurs fichiers simultanément avec traitement parallèle
    </a>

-   <a href="user-guide/formats/" class="card-link" markdown="1" aria-label="Guide utilisateur : formats de documents pris en charge">
    :material-format-list-bulleted:{ .lg .middle } __Support multi-formats__

    ---

    PDFs, documents Word, PowerPoints, fichiers Excel, HTML, Markdown, images et plus encore
    </a>

-   <a href="user-guide/features/#formats-dexport" class="card-link" markdown="1" aria-label="Guide utilisateur : section Formats d'export">
    :material-export:{ .lg .middle } __Formats d'export multiples__

    ---

    Exportez vers Markdown, HTML, JSON, DocTags, Document Tokens, RAG Chunks ou texte brut
    </a>

-   <a href="user-guide/features/#extraction-des-tableaux" class="card-link" markdown="1" aria-label="Guide utilisateur : section Extraction d'images et tableaux">
    :material-image-multiple:{ .lg .middle } __Extraction d'images et tableaux__

    ---

    Extrayez les images intégrées et les tableaux avec export CSV
    </a>

-   <a href="user-guide/features/#decoupage-pour-rag" class="card-link" markdown="1" aria-label="Guide utilisateur : section Segmentation RAG">
    :material-puzzle:{ .lg .middle } __Segmentation prête pour RAG__

    ---

    Générez des segments de document optimisés pour les applications RAG
    </a>

-   <a href="user-guide/features/#ocr-reconnaissance-optique-de-caracteres" class="card-link" markdown="1" aria-label="Guide utilisateur : section OCR">
    :material-eye:{ .lg .middle } __OCR avancé__

    ---

    Plusieurs backends OCR avec support d'accélération GPU
    </a>

-   <a href="user-guide/features/#historique-des-conversions" class="card-link" markdown="1" aria-label="Guide utilisateur : section Historique des conversions">
    :material-history:{ .lg .middle } __Historique des conversions__

    ---

    Accédez aux documents précédemment convertis à tout moment
    </a>

-   <a href="user-guide/features/#panneau-des-statistiques" class="card-link" markdown="1" aria-label="Guide utilisateur : section Statistiques de conversion">
    :material-chart-line:{ .lg .middle } __Statistiques de conversion__

    ---

    Panneau d'analytique avec débit, utilisation du stockage et métriques de performance
    </a>

</div>


## Démarrage rapide

Consultez **[Bien démarrer](getting-started/index.md)** pour installer et exécuter Duckling avec Docker ou en développement local. Un guide court est dans **[Démarrage rapide](getting-started/quickstart.md)**.

## Documentation

- **[Bien démarrer](getting-started/index.md)** - Installation et démarrage
- **[Guide d'utilisation](user-guide/index.md)** - Fonctions et configuration
- **[Documentation Docling](docling/index.md)** - Documentation Docling (amont)
- **[Référence API](api/index.md)** - Documentation de l'API
- **[Architecture](architecture/index.md)** - Conception et composants
- **[Déploiement](deployment/index.md)** - Mise en production
- **[Contribuer](contributing/index.md)** - Comment contribuer
- **[Journal des modifications](changelog.md)** - Historique des versions

## Remerciements

- [Docling](https://github.com/docling-project/docling) (IBM) pour le moteur de conversion
- [React](https://react.dev/) pour l'interface
- [Flask](https://flask.palletsprojects.com/) pour l'API
- [Tailwind CSS](https://tailwindcss.com/) pour le style
- [Framer Motion](https://www.framer.com/motion/) pour les animations

