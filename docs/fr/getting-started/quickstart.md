# Démarrage rapide

Démarrez avec Duckling en 5 minutes.

## Démarrer l'application

Choisissez votre méthode préférée :

=== "Docker (recommeté)"

    Le moyen le plus rapide de démarrer - aucune dépendance à installer !

    **Option 1 : Images préconstruites (le plus rapide)**
    ```bash
    # Download the compose file
    curl -O https://raw.githubusercontent.com/davidgs/duckling/main/docker-compose.prebuilt.yml

    # Start Duckling
    docker-compose -f docker-compose.prebuilt.yml up -d
    ```

    **Option 2 : Construire localement**
    ```bash
    # Clone and start
    git clone https://github.com/davidgs/duckling.git
    cd duckling
    docker-compose up --build
    ```

    L'interface sera disponible à `http://localhost:3000`

    !!! tip "Premier démarrage"
        Le premier démarrage peut prendre quelques minutes pendant que Docker télécharge/construit les images.

=== "Configuration manuelle"

    ### Terminal 1 : Backend

    ```bash
    cd backend
    source venv/bin/activate  # Windows: venv\Scripts\activate
    python duckling.py
    ```

    L'API sera disponible à `http://localhost:5001`

    ### Terminal 2 : Frontend

    ```bash
    cd frontend
    npm run dev
    ```

    L'interface sera disponible à `http://localhost:3000`

## Votre première conversion

### 1. Ouvrir l'application

Accédez à `http://localhost:3000` dans votre navigateur.

<figure markdown="span">
  ![Duckling Interface](../assets/screenshots/ui/main-english.png){ loading=lazy }
  <figcaption>L'interface principale de Duckling</figcaption>
</figure>

### 2. Télécharger un document

Glissez-déposez un PDF, document Word ou image dans la zone de dépôt, ou cliquez pour parcourir.

<figure markdown="span">
  ![Uploading Document](../assets/screenshots/ui/dropzone-uploading.svg){ loading=lazy }
  <figcaption>Indicateur de progression du téléchargement</figcaption>
</figure>

### 3. Suivre la progression

La progression de la conversion sera affichée en temps réel.

<figure markdown="span">
  ![Conversion Progress](../assets/screenshots/features/conversion-progress.svg){ loading=lazy }
  <figcaption>Progression de conversion en temps réel</figcaption>
</figure>

### 4. Télécharger les résultats

Une fois terminé, choisissez votre format d'exportation :

<figure markdown="span">
  ![Conversion Complete](../assets/screenshots/features/conversion-complete.svg){ loading=lazy }
  <figcaption>Conversion terminée avec options d'export</figcaption>
</figure>

- **Markdown** - Idéal pour la documentation
- **HTML** - Sortie prête pour le web
- **JSON** - Structure complète du document
- **Texte brut** - Extraireion de texte simple

## Configuration de base

Cliquez sur :material-cog: **Paramètres** bouton pour configurer :

### Paramètres OCR

| Paramètre | Par défaut | Description |
|---------|---------|-------------|
| Activé | `true` | Activer l'OCR pour les documents numérisés |
| Backend | `easyocr` | Moteur OCR à utiliser |
| Langue | `en` | Langue principale |

### Paramètres des tableaux

| Paramètre | Par défaut | Description |
|---------|---------|-------------|
| Activé | `true` | Extraire les tableaux des documents |
| Mode | `précis` | Niveau de précision de détection |

### Paramètres des images

| Paramètre | Par défaut | Description |
|---------|---------|-------------|
| Extraire | `true` | Extraire les images intégrées |
| Échelle | `1.0` | Échelle de sortie des images |

## Traitement par lots

Pour convertir plusieurs fichiers à la fois :

1. Activer **Mode lot** dans l'en-tête
2. Glissez plusieurs fichiers dans la zone de dépôt
3. Tous les fichiers seront traités simultanément

<figure markdown="span">
  ![Mode lot](../assets/screenshots/ui/dropzone-batch.png){ loading=lazy }
  <figcaption>Mode lot avec plusieurs fichiers</figcaption>
</figure>

!!! tip "Performances"
    Le traitement par lots utilise une file d'attente de tâches avec un maximum de 2 conversions simultanées pour éviter l'épuisement de la mémoire.

## Utiliser l'API

Pour un accès programmatique, utilisez l'API REST :

```bash
# Upload and convert a document
curl -X POST http://localhost:5001/api/convert \
  -F "file=@document.pdf"

# Response
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

Consultez la [Référence API](../api/index.md) pour la documentation complète.

## Prochaines étapes

- [Fonctionnalités](../user-guide/features.md) - Explorer toutes les fonctionnalités
- [Configuration](../user-guide/configuration.md) - Paramètres avancés
- [Référence API](../api/index.md) - Intégrer à vos applications

