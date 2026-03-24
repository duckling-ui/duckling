# Journal des modifications

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère au [Versionnage Sémantique](https://semver.org/spec/v2.0.0.html).

**Dernière version :** [0.0.10a](https://github.com/davidgs/duckling/releases/tag/v0.0.10a) (2026-03-23)

## [Non publié]

### Corrigé

- **Tests frontend** : le test de navigation iframe de `DocsPanel` attend que l’écouteur `message` soit enregistré après la fin du `fetch` mocké et utilise un délai `waitFor` plus long pour garder la CI stable sur des exécuteurs plus lents.

### Prévu

- Authentification des utilisateurs
- Intégration du stockage cloud
- Modèles de conversion
- Limitation du débit de l'API
- WebSocket pour les mises à jour en temps réel
- Bascule thème sombre/clair
- Raccourcis clavier
- Améliorations d'accessibilité (WCAG 2.1)

## [0.0.10a] - 2026-03-23

### Corrigé

- **Dépendances backend** : Un seul fichier `backend/requirements.txt` pour l'API et les builds MkDocs in-app ; suppression du doublon `backend/requirements-docs.txt`.

### Modifié

- **Navigation de la documentation** : Passage des onglets horizontaux en haut à une barre latérale gauche unique avec navigation en arbre repliable ; chaque catégorie principale (Accueil, Démarrage, etc.) peut être développée ou repliée.
- **Tuiles des fonctionnalités clés** : Chaque tuile de fonctionnalité sur la page d'accueil de la documentation est maintenant un lien cliquable vers sa documentation détaillée (page Fonctionnalités ou Formats).
- **CONTRIBUTING.md** : Ajout de l'exigence de signature DCO (Developer Certificate of Origin) pour tous les commits.
- **Documentation de contribution** : Traductions complètes pour l'allemand (de), l'espagnol (es) et le français (fr) ; toutes les locales ont maintenant un contenu cohérent et complet incluant les exigences DCO.

### Sécurité

- Corrigé le path traversal Rollup (GHSA-mw96-cpmx-2vgc) et le ReDoS Minimatch (GHSA-3ppc-4f35-3m26) via les overrides npm dans le frontend : `rollup >=4.59.0`, `minimatch 9.0.6` pour `@typescript-eslint/typescript-estree`.
- Corrigé Werkzeug safe_join pour les noms de périphériques Windows dans les chemins multi-segments (CVE-2026-27199, GHSA-29vq-49wr-vm6x) : werkzeug 3.1.4 → 3.1.6.
- Corrigé l'en-tête Vary: Cookie de session Flask lors de l'utilisation de l'opérateur `in` (CVE-2026-27205) : flask 3.0.0 → 3.1.3.
- **Prévention SSRF** : Validation des URL avant les requêtes sortantes dans `download_from_url`, `download_from_url_with_images` et `download_image` ; bloque loopback, IPs privées, link-local, metadata et schémas dangereux.
- **Corrections de sécurité CodeQL** :
  - SSRF : `validate_url_safe_for_request` retourne maintenant l'URL validée ; tous les appels `requests.get` utilisent la valeur retournée pour satisfaire l'analyse de flux de données.
  - ReDoS : Extraction d'images HTML limitée à 5 Mo avant le traitement regex pour atténuer les regex polynomiales sur le contenu contrôlé par l'utilisateur.
  - Path traversal : `delete_output_folder` utilise maintenant `validate_job_id` et `get_validated_output_dir` des utilitaires de sécurité au lieu de vérifications manuelles.
  - Exposition d'informations : Réponses d'erreur de l'API des paramètres sanitaires via `_sanitize_error_for_client` pour éviter les fuites de stack trace ou de données sensibles.

## [0.0.10a] - 2026-02-24

### Ajouté

- **Workflow de publication d'images Docker** : GitHub Action s'exécute lorsque les PR sont fusionnés dans `main`, construisant des images multi-plateformes et les poussant vers Docker Hub et GitHub Container Registry (nécessite les secrets `DOCKERHUB_USERNAME` et `DOCKERHUB_TOKEN`).
- **Générer les fragments maintenant** : Bouton dans l'onglet Fragments RAG pour générer des fragments à la demande pour les documents terminés (`POST /api/history/{job_id}/generate-chunks`)
- **Déduplication par contenu** : Même fichier + mêmes paramètres affectant le document réutilisent le contenu stocké au lieu de reconvertir
  - Cache hit : créer symlink, charger métadonnées, terminer immédiatement (pas d'exécution Docling)
  - Cache miss : exécuter conversion, déplacer sortie vers le magasin de contenu, créer symlink
  - Migration base de données `scripts/migrate_add_content_hash.py` ajoute la colonne `content_hash`
- **Statistiques et métriques de conversion** : Statistiques d'historique étendues pour l'analyse d'utilisation Docling et Duckling
  - `GET /api/history/stats` retourne `avg_processing_seconds`, `ocr_backend_breakdown`, `output_format_breakdown`, `performance_device_breakdown`, `chunking_enabled_count`, `error_category_breakdown`, `source_type_breakdown` et `queue_depth`
  - Migration base de données `scripts/migrate_add_stats_columns.py` ajoute les colonnes de stats à la table conversions
  - Le panneau Historique affiche le temps de traitement moyen et la profondeur de file d'attente lorsqu'ils sont disponibles
- **Panneau de statistiques** : Visualiseur dédié pour les statistiques de conversion (bouton d'en-tête, « Voir les statistiques complètes » depuis Historique)
- **Statistiques étendues** : Métriques matérielles et de performance dans le panneau Statistiques
  - Section système : type de matériel (CPU/CUDA/MPS), nombre de CPU, utilisation CPU actuelle, infos GPU
  - Pages/sec moyenne et pages/sec par CPU
  - Distribution du temps de conversion (médiane, 95e, 99e percentile)
  - Graphique pages/sec au fil du temps
  - Utilisation CPU moyennée pendant chaque conversion (stockée en DB)
  - Migration base de données `scripts/migrate_add_cpu_usage_column.py` ajoute la colonne `cpu_usage_avg_during_conversion`
  - L'utilisation CPU est maintenant spécifique au processus (processus backend Duckling, exécute Docling), pas système
  - Config par conversion stockée : `performance_device_used` (résolu de « auto » à la fin), `images_classify_enabled`
  - Migration base de données `scripts/migrate_add_config_columns.py` ajoute ces colonnes
  - Répartition des stats par matériel, backend OCR, classificateur d'images (pages/sec, temps de conversion par config)
- Support des langues de l'interface (Anglais `en`, Espagnol `es`, Français `fr`, Allemand `de`) avec sélecteur de langue.
- Documentation MkDocs multilingue (Anglais, Espagnol, Français, Allemand) servie sous `/api/docs/site/<locale>/`.
- Libellés de catégories du panneau Dropzone (Documents, Web, Images, Données) maintenant entièrement internationalisés.
- Section documentation Docling dans MkDocs (sous-ensemble curé et vendu de la documentation Docling upstream + script de synchronisation).
- **Paramètres utilisateur par session** : Paramètres utilisateur stockés par session dans la base de données au lieu d'un fichier partagé.

### Sécurité

- Corrigé les vulnérabilités de sécurité frontend (esbuild GHSA-67mh-4wv8-2f99) : Vite 5→7, Vitest 1→4 et dépendances associées mises à jour.

### Modifié

- Point d'entrée du backend renommé de `app.py` à `duckling.py` pour plus de clarté.
- Nom de l'application Flask changé en « duckling » (affiche « Serving Flask app 'duckling' »).

### Corrigé

- La navigation de la documentation affiche maintenant des noms de pages entièrement localisés dans toutes les langues prises en charge.
- Les libellés de catégories de formats de fichiers du panneau Dropzone se traduisent maintenant correctement selon la langue sélectionnée.
- Amélioration de l'extraction des titres de pages de documentation avec un meilleur repli vers les noms traduits.
- Les liens prev/suivant du pied du panneau de documentation intégrée restent dans la catégorie actuelle de la barre latérale, et la navigation dans la documentation intégrée garde la sélection de la barre latérale synchronisée.
- Corrigé l'échec de reconstruction de la documentation intégrée avec `cannot access local variable 'shutil'` lors de la construction du site MkDocs.
- La reconstruction de la documentation du backend préfère maintenant l'environnement MkDocs `./venv` local du dépôt pour s'assurer que les plugins requis (comme `i18n`) sont disponibles.
- Corrigé le clic sur une entrée d'historique qui ne chargeait pas le document ; utilise maintenant l'endpoint de chargement d'historique (disque) au lieu de l'endpoint de résultat en mémoire.
- Lorsque `document_json_path` est manquant dans la DB, le chargement d'historique trouve et charge `*.document.json` depuis le répertoire de sortie pour que tous les éléments d'historique se chargent, pas seulement le premier.
- Le panneau de visualisation de documents se rafraîchit maintenant lors du chargement d'un élément d'historique différent (utilise la clé de composant pour remonter avec un état frais).
- Mis à jour `vitest.config.ts` pour la compatibilité Vitest 4.
- Exigence de version Node.js CI/CD mise à jour vers 22 (requis pour Vite 7).

## [0.0.9] - 2026-01-08

### Ajouté

- **Personnalisation** : Logo Duckling et affichage de version dans l'en-tête.
- **Conversion de documents par URL** : Conversion depuis des URLs avec extraction automatique d'images pour HTML.
- **Options d'enrichissement de documents** : Enrichissement de code, formules, classification d'images, description d'images.
- **Téléchargement préalable des modèles d'enrichissement** : Télécharger les modèles IA avant le traitement.
- **Galerie de prévisualisation d'images** : Miniatures visuelles avec visionneuse lightbox.
- **Installation automatique des backends OCR** : Installation en un clic pour les backends pip.
- **Prévisualisation spécifique au format** : Le panneau de prévisualisation affiche le contenu dans le format d'export sélectionné.
- **Mode prévisualisation rendu vs brut** : Bascule pour HTML et Markdown.
- **Support Docker amélioré** : Dockerfiles multi-étapes, variantes docker-compose, builds multi-plateformes.

### Corrigé

- Récupération de contenu multi-worker (images, tableaux, résultats).
- Prévisualisation HTML dans l'interface.
- Extraction d'images URL pour les attributs `src` non quotés.
- Le panneau de documentation sert maintenant le site MkDocs pré-construit.
- Variables d'environnement et chargement `.env`.
- Extensions de fichiers insensibles à la casse.
- Score de confiance et sélection du backend OCR.

## [0.0.8] - 2026-01-07

### Modifié

- **Renommé** : Projet renommé de « Docling UI » à « Duckling »
  - Toute la documentation, le code et les fichiers de configuration mis à jour
  - Marque mise à jour dans toute l'application

## [0.0.7] - 2026-01-07

### Ajouté

- **Documentation MkDocs** : Migration de la documentation vers MkDocs avec thème Material
  - Site de documentation moderne et recherchable
  - Bascule thème sombre/clair
  - Support des diagrammes Mermaid
  - Navigation et organisation améliorées

### Modifié

- Structure de la documentation réorganisée pour une meilleure navigation
- Tous les diagrammes convertis au format Mermaid pour un rendu en direct

## [0.0.6] - 2025-12-11

### Sécurité

- **CRITIQUE** : Corrigé le mode debug Flask activé par défaut en production
  - Le mode debug est maintenant contrôlé par la variable d'environnement `FLASK_DEBUG` (par défaut : false)
  - Le binding d'hôte par défaut est `127.0.0.1` au lieu de `0.0.0.0`
- **ÉLEVÉ** : Dépendances vulnérables mises à jour
  - `flask-cors` : 4.0.0 → 6.0.0 (CVE-2024-1681, CVE-2024-6844, CVE-2024-6866, CVE-2024-6839)
  - `gunicorn` : 21.2.0 → 23.0.0 (CVE-2024-1135, CVE-2024-6827)
  - `werkzeug` : 3.0.1 → 3.1.4 (CVE-2024-34069, CVE-2024-49766, CVE-2024-49767, CVE-2025-66221)
- **MOYEN** : Protection contre le path traversal ajoutée aux endpoints de service de fichiers
  - Le service d'images valide que les chemins n'échappent pas aux répertoires autorisés
  - Bloque les séquences de traversée de répertoires (`..`)
- **MOYEN** : Sanitisation des requêtes SQL améliorée
  - Les requêtes de recherche échappent maintenant les wildcards LIKE
  - Limites de longueur de requête ajoutées
- Ajout de `SECURITY.md` complet avec :
  - Résumé d'audit de sécurité
  - Liste de contrôle de déploiement en production
  - Documentation des variables d'environnement
  - Lignes directrices de signalement des vulnérabilités

### Modifié

- Le backend utilise maintenant des variables d'environnement pour toute la configuration sensible à la sécurité
- Hôte par défaut changé de `0.0.0.0` à `127.0.0.1` pour des valeurs par défaut plus sûres

## [0.0.5] - 2025-12-10

### Ajouté

- **Traitement par lots** : Télécharger et convertir plusieurs fichiers à la fois
  - Bascule du mode lots dans l'en-tête
  - Traiter plusieurs documents simultanément

- **Extraction d'images et de tableaux** :
  - Extraire les images intégrées des documents
  - Télécharger les images individuellement
  - Extraire les tableaux avec préservation complète des données
  - Exporter les tableaux au format CSV
  - Voir les aperçus de tableaux dans l'interface

- **Support RAG/Fragmentation** :
  - Fragmentation de documents pour les applications RAG
  - Tokens max configurables par fragment (64-8192)
  - Option de fusion des fragments sous-dimensionnés
  - Télécharger les fragments en JSON

- **Formats d'export supplémentaires** :
  - Tokens de document (`.tokens.json`)
  - Fragments RAG (`.chunks.json`)
  - Export DocTags amélioré

- **Options OCR avancées** :
  - Plusieurs backends OCR : EasyOCR, Tesseract, macOS Vision, RapidOCR
  - Support d'accélération GPU (EasyOCR)
  - Seuil de confiance configurable (0-1)
  - Contrôle du seuil de zone bitmap
  - Support de plus de 28 langues

- **Options de structure de tableaux** :
  - Modes de détection Rapide vs Précise
  - Configuration de correspondance des cellules
  - Bascule d'extraction de structure

- **Options de génération d'images** :
  - Générer les images de page
  - Extraire les images de figures
  - Extraire les images de tableaux
  - Échelle d'image configurable (0.1x - 4.0x)

- **Options de performance/accélérateur** :
  - Sélection de périphérique : Auto, CPU, CUDA, MPS (Apple Silicon)
  - Configuration du nombre de threads (1-32)
  - Paramètre de timeout de document

- **Nouveaux endpoints API** :
  - `POST /api/convert/batch` - Conversion par lots
  - `GET /api/convert/<job_id>/images` - Lister les images extraites
  - `GET /api/convert/<job_id>/images/<id>` - Télécharger l'image
  - `GET /api/convert/<job_id>/tables` - Lister les tableaux extraits
  - `GET /api/convert/<job_id>/tables/<id>/csv` - Télécharger le CSV du tableau
  - `GET /api/convert/<job_id>/tables/<id>/image` - Télécharger l'image du tableau
  - `GET /api/convert/<job_id>/chunks` - Obtenir les fragments du document
  - `GET/PUT /api/settings/performance` - Paramètres de performance
  - `GET/PUT /api/settings/chunking` - Paramètres de fragmentation
  - `GET /api/settings/formats` - Lister tous les formats pris en charge

### Modifié

- **Panneau des paramètres** : Complètement repensé avec toutes les nouvelles options
- **Options d'export** : Améliorées avec des onglets pour différents types de contenu
- **DropZone** : Mis à jour avec les catégories de format et le support du mode lots
- **Service de conversion** : Refactorisation majeure pour les options de pipeline dynamiques

### Corrigé

- Le calcul du score de confiance utilise maintenant les prédictions au niveau du cluster
- Meilleure gestion du succès partiel de conversion

## [0.0.4] - 2025-12-10

### Ajouté

- **Support OCR** : Intégration OCR complète avec EasyOCR
  - Support de plus de 14 langues
  - Option Forcer OCR de page complète
  - Paramètres OCR configurables
- **Calcul de confiance amélioré** : Confiance moyenne des prédictions de mise en page

### Modifié

- Service de conversion mis à jour pour utiliser les options de pipeline configurables
- Panneau des paramètres amélioré avec les options OCR

## [0.0.3] - 2025-12-10

### Ajouté

- Version initiale de Duckling
- **Fonctionnalités frontend** :
  - Téléchargement de fichiers par glisser-déposer
  - Progression de conversion en temps réel
  - Options d'export multi-format
  - Panneau des paramètres
  - Panneau d'historique des conversions
  - Thème sombre avec accent turquoise
  - Design responsive
  - Transitions animées

- **Fonctionnalités backend** :
  - API REST Flask avec CORS
  - Conversion de documents asynchrone
  - Historique basé sur SQLite
  - Gestion du téléchargement de fichiers
  - Paramètres configurables
  - Endpoint de vérification de santé

- **Formats d'entrée pris en charge** :
  - PDF, Word, PowerPoint, Excel
  - HTML, Markdown, CSV
  - Images (PNG, JPG, TIFF, etc.)
  - AsciiDoc, XML

- **Formats d'export** :
  - Markdown, HTML, JSON
  - DocTags, texte brut

- **Expérience développeur** :
  - Suites de tests complètes
  - Support Docker
  - TypeScript
  - Configuration ESLint

### Sécurité

- Validation des entrées pour le téléchargement de fichiers
- Restrictions de type de fichier
- Limites de taille maximale des fichiers
- Gestion sécurisée des noms de fichiers

[Unreleased]: https://github.com/davidgs/duckling/compare/v0.0.10a...HEAD
[0.0.10a]: https://github.com/davidgs/duckling/compare/v0.0.10...v0.0.10a
[0.0.10a]: https://github.com/davidgs/duckling/compare/v0.0.9...v0.0.10
[0.0.9]: https://github.com/davidgs/duckling/compare/v0.0.8...v0.0.9
[0.0.8]: https://github.com/davidgs/duckling/compare/v0.0.7...v0.0.8
[0.0.7]: https://github.com/davidgs/duckling/compare/v0.0.6...v0.0.7
[0.0.6]: https://github.com/davidgs/duckling/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/davidgs/duckling/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/davidgs/duckling/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/davidgs/duckling/releases/tag/v0.0.3
