# Premiers pas

Bienvenue sur Duckling ! Cette section vous aide à démarrer rapidement.

!!! tip "Démarrage le plus rapide"
    **Avec Docker ?** Une seule commande suffit :
    ```bash
    curl -O https://raw.githubusercontent.com/duckling-ui/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Ouvrez ensuite [http://localhost:3000](http://localhost:3000) dans votre navigateur.

## Prérequis

=== "Docker (recommandé)"

    - **Docker 20.10+**
    - **Docker Compose 2.0+**

    C’est tout ! Pas besoin de Python ni de Node.js.

=== "Développement local"

    - **Python 3.10+** (3.13 recommandé)
    - **Node.js 18+**
    - **npm ou yarn**
    - **Git**

## Options d’installation

Choisissez la méthode qui vous convient le mieux :

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } __Docker (recommandé)__

    ---

    Le moyen le plus rapide de commencer. Déploiement en une commande avec des images préconstruites.

    [:octicons-arrow-right-24: Guide Docker](docker.md)

-   :material-rocket-launch:{ .lg .middle } __Démarrage rapide__

    ---

    Démarrer en 5 minutes avec l’essentiel

    [:octicons-arrow-right-24: Démarrage rapide](quickstart.md)

-   :material-code-braces:{ .lg .middle } __Développement local__

    ---

    Configurer un environnement de développement local pour personnaliser et contribuer

    [:octicons-arrow-right-24: Guide d’installation](installation.md)

</div>

## Et après ?

Après l’installation, explorez :

1. **[Fonctionnalités](../user-guide/features.md)** – Découvrir toutes les capacités
2. **[Configuration](../user-guide/configuration.md)** – Adapter les paramètres à vos besoins
3. **[Référence API](../api/index.md)** – Intégrer à vos applications

