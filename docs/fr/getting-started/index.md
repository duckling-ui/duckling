# Bien démarrer

Bienvenue dans Duckling ! Cette section vous aidera à démarrer rapidement.

!!! tip "Méthode la plus rapide"
    **Utilisez Docker ?** Exécutez cette commande unique et c'est terminé :
    ```bash
    curl -O https://raw.githubusercontent.com/davidgs/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Ensuite, ouvrez [http://localhost:3000](http://localhost:3000) dans votre navigateur.

## Prérequis

=== "Docker (Recommandé)"

    - **Docker 20.10+**
    - **Docker Compose 2.0+**

    C'est tout ! Python ou Node.js ne sont pas requis.

=== "Développement local"

    - **Python 3.10+** (3.13 recommandé)
    - **Node.js 18+**
    - **npm ou yarn**
    - **Git**

## Options d'installation

Choisissez la méthode d'installation qui vous convient le mieux :

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } __Docker (Recommandé)__

    ---

    Le moyen le plus rapide de démarrer. Déploiement en une commande avec images pré-construites.

    [:octicons-arrow-right-24: Guide Docker](docker.md)

-   :material-rocket-launch:{ .lg .middle } __Démarrage rapide__

    ---

    Démarrez en 5 minutes avec l'essentiel

    [:octicons-arrow-right-24: Démarrage rapide](quickstart.md)

-   :material-code-braces:{ .lg .middle } __Développement local__

    ---

    Configurez un environnement de développement local pour la personnalisation et la contribution

    [:octicons-arrow-right-24: Guide d'installation](installation.md)

</div>

## Prochaines étapesAprès l'installation, explorez :1. **[Fonctionnalités](../user-guide/features.md)** - Découvrez toutes les capacités
2. **[Configuration](../user-guide/configuration.md)** - Personnalisez les paramètres selon vos besoins
3. **[Référence API](../api/index.md)** - Intégrez avec vos applications