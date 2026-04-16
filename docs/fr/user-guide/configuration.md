# Guide de configuration

Référence complète de toutes les options de configuration de Duckling.

## Variables d'environnement

Créez un fichier `.env` dans le répertoire `backend` :

```env
# Flask Configuration
FLASK_ENV=development          # development | production | testing
SECRET_KEY=your-secret-key     # Required for production
DEBUG=True                     # Enable debug mode

# File Handling
MAX_CONTENT_LENGTH=104857600   # Max upload size in bytes (100MB default)

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///history.db
```

### Environnement de production

```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key-here
DEBUG=False
MAX_CONTENT_LENGTH=209715200   # 200MB for production
```

!!! danger "Avertissement de sécurité"
    N'utilisez jamais la `SECRET_KEY` par défaut en production. Générez une clé aléatoire sécurisée.

---

## Paramètres OCR

L'OCR (reconnaissance optique de caractères) extrait le texte des images et des documents numérisés.

### Options de configuration

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `enabled` | boolean | `true` | Activer ou désactiver l'OCR |
| `backend` | string | `"easyocr"` | Moteur OCR à utiliser |
| `language` | string | `"en"` | Langue principale de reconnaissance |
| `force_full_page_ocr` | boolean | `false` | OCR sur toute la page ou zones détectées |
| `use_gpu` | boolean | `false` | Accélération GPU (EasyOCR uniquement) |
| `confidence_threshold` | float | `0.5` | Confiance minimale des résultats (0–1) |
| `bitmap_area_threshold` | float | `0.05` | Ratio de surface minimal pour l'OCR bitmap (0–1) |

### Moteurs OCR

=== "EasyOCR"

    Idéal pour les documents multilingues exigeant la précision.

    ```json
    {
      "ocr": {
        "backend": "easyocr",
        "use_gpu": true,
        "language": "en"
      }
    }
    ```

    - **GPU** : oui (CUDA)
    - **Langues** : 80+
    - **Remarque** : des problèmes d'initialisation peuvent survenir sur certains systèmes

=== "Tesseract"

    Moteur OCR classique et fiable pour des documents simples.

    ```json
    {
      "ocr": {
        "backend": "tesseract",
        "language": "eng"
      }
    }
    ```

    - **GPU** : non
    - **Langues** : 100+
    - **Prérequis** : Tesseract installé sur le système

=== "macOS Vision"

    OCR macOS native via le framework Vision d'Apple.

    ```json
    {
      "ocr": {
        "backend": "ocrmac",
        "language": "en"
      }
    }
    ```

    - **GPU** : utilise l'Apple Neural Engine
    - **Prérequis** : macOS 10.15+
    - **Codes langue** : Duckling accepte les codes courts (`en`, `de`, `fr`, etc.) et les normalise en balises de locale Vision (par ex. `en-US`) pendant la conversion.

=== "RapidOCR"

    OCR rapide et léger avec ONNX Runtime.

    ```json
    {
      "ocr": {
        "backend": "rapidocr",
        "language": "en"
      }
    }
    ```

    - **GPU** : non
    - **Langues** : limité

### Langues prises en charge

| Code | Langue | Code | Langue |
|------|--------|------|--------|
| `en` | Anglais | `ja` | Japonais |
| `de` | Allemand | `zh` | Chinois (simplifié) |
| `fr` | Français | `zh-tw` | Chinois (traditionnel) |
| `es` | Espagnol | `ko` | Coréen |
| `it` | Italien | `ar` | Arabe |
| `pt` | Portugais | `hi` | Hindi |
| `nl` | Néerlandais | `th` | Thaï |
| `pl` | Polonais | `vi` | Vietnamien |
| `ru` | Russe | `tr` | Turc |

---

## Paramètres des tableaux

Configurez la détection et l'extraction des tableaux dans les documents.

### Options de configuration

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `enabled` | boolean | `true` | Activer la détection de tableaux |
| `structure_extraction` | boolean | `true` | Conserver la structure du tableau |
| `mode` | string | `"accurate"` | Mode de détection |
| `do_cell_matching` | boolean | `true` | Associer le contenu des cellules à la structure |

### Modes de détection

=== "Mode précis"

    ```json
    {
      "tables": {
        "enabled": true,
        "mode": "accurate",
        "do_cell_matching": true
      }
    }
    ```

    - Détection de tableaux plus précise
    - Meilleure reconnaissance des limites de cellules
    - Traitement plus lent
    - Recommandé pour les tableaux complexes

=== "Mode rapide"

    ```json
    {
      "tables": {
        "enabled": true,
        "mode": "fast",
        "do_cell_matching": false
      }
    }
    ```

    - Traitement plus rapide
    - Adapté aux tableaux simples
    - Peut manquer des structures complexes

---

## Paramètres des images

Configurez l'extraction et le traitement des images.

### Options de configuration

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `extract` | boolean | `true` | Extraire les images intégrées |
| `classify` | boolean | `true` | Classifier et étiqueter les images |
| `generate_page_images` | boolean | `false` | Créer une image par page |
| `generate_picture_images` | boolean | `true` | Extraire les illustrations en fichiers |
| `generate_table_images` | boolean | `true` | Extraire les tableaux sous forme d'images |
| `images_scale` | float | `1.0` | Facteur d'échelle des images (0,1 à 4,0) |

### Exemples de configuration

=== "Haute qualité"

    ```json
    {
      "images": {
        "extract": true,
        "classify": true,
        "generate_page_images": true,
        "generate_picture_images": true,
        "generate_table_images": true,
        "images_scale": 2.0
      }
    }
    ```

=== "Minimal (texte uniquement)"

    ```json
    {
      "images": {
        "extract": false,
        "classify": false,
        "generate_page_images": false,
        "generate_picture_images": false,
        "generate_table_images": false
      }
    }
    ```

---

## Paramètres de performances

Optimisez la vitesse de traitement et l'utilisation des ressources.

### Options de configuration

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `device` | string | `"auto"` | Périphérique de traitement |
| `num_threads` | int | `4` | Fils CPU (1–32) |
| `document_timeout` | int/null | `null` | Durée maximale de traitement en secondes |

### Options des périphériques

| Périphérique | Description | Idéal pour |
|---------------|-------------|------------|
| `auto` | Choisit automatiquement le meilleur périphérique | Usage général |
| `cpu` | Force le traitement CPU | Serveurs sans GPU |
| `cuda` | Accélération GPU NVIDIA | Linux/Windows avec GPU NVIDIA |
| `mps` | Apple Metal Performance Shaders | macOS avec Apple Silicon |

### Exemples de configuration

=== "Hautes performances (GPU)"

    ```json
    {
      "performance": {
        "device": "cuda",
        "num_threads": 8,
        "document_timeout": null
      }
    }
    ```

=== "Ressources limitées"

    ```json
    {
      "performance": {
        "device": "cpu",
        "num_threads": 2,
        "document_timeout": 60
      }
    }
    ```

=== "Apple Silicon"

    ```json
    {
      "performance": {
        "device": "mps",
        "num_threads": 4,
        "document_timeout": null
      }
    }
    ```

---

## Paramètres de découpage (chunking)

Configurez le découpage de document pour les applications RAG.

### Options de configuration

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `enabled` | boolean | `false` | Activer le découpage |
| `max_tokens` | int | `512` | Nombre maximal de jetons par segment |
| `merge_peers` | boolean | `true` | Fusionner les petits segments |

### Exemples de configuration

=== "Optimisé RAG"

    ```json
    {
      "chunking": {
        "enabled": true,
        "max_tokens": 512,
        "merge_peers": true
      }
    }
    ```

=== "Grandes fenêtres de contexte"

    ```json
    {
      "chunking": {
        "enabled": true,
        "max_tokens": 2048,
        "merge_peers": false
      }
    }
    ```

---

## Paramètres de sortie

Définissez le format de sortie par défaut.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `default_format` | string | `"markdown"` | Format d'export par défaut |

---

## Exemple de configuration complet

```json
{
  "ocr": {
    "enabled": true,
    "backend": "easyocr",
    "language": "en",
    "force_full_page_ocr": false,
    "use_gpu": false,
    "confidence_threshold": 0.5,
    "bitmap_area_threshold": 0.05
  },
  "tables": {
    "enabled": true,
    "structure_extraction": true,
    "mode": "accurate",
    "do_cell_matching": true
  },
  "images": {
    "extract": true,
    "classify": true,
    "generate_page_images": false,
    "generate_picture_images": true,
    "generate_table_images": true,
    "images_scale": 1.0
  },
  "performance": {
    "device": "auto",
    "num_threads": 4,
    "document_timeout": null
  },
  "chunking": {
    "enabled": false,
    "max_tokens": 512,
    "merge_peers": true
  },
  "output": {
    "default_format": "markdown"
  }
}
```

---

## Configuration via l'API

### Obtenir les paramètres actuels

```bash
curl http://localhost:5001/api/settings
```

### Mettre à jour les paramètres

```bash
curl -X PUT http://localhost:5001/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "ocr": {"backend": "tesseract"},
    "performance": {"num_threads": 8}
  }'
```

### Réinitialiser aux valeurs par défaut

```bash
curl -X POST http://localhost:5001/api/settings/reset
```

---

## Dépannage

### L'OCR ne fonctionne pas

1. **Erreur d'initialisation EasyOCR** : passez à `ocrmac` (macOS) ou `tesseract`
2. **Erreurs GPU** : définissez `use_gpu: false`
3. **Résultats peu confiants** : baissez `confidence_threshold`

### Traitement lent

1. Réduisez `images_scale` à `0,5`
2. Utilisez `mode: "fast"` pour les tableaux
3. Désactivez `generate_page_images`
4. Augmentez `num_threads`

### Problèmes de mémoire

1. Activez `document_timeout` (par ex. 120 secondes)
2. Traitez moins de fichiers par lot
3. Réduisez `images_scale`
4. Désactivez le chunking si inutile
