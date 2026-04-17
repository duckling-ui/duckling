# Déploiement Docker

Déployez Duckling avec Docker pour une mise en place rapide et une isolation.

!!! success "TL;DR – Démarrage en une commande"
    ```bash
    curl -O https://raw.githubusercontent.com/duckling-ui/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Ouvrez ensuite `http://localhost:3000` 🎉

## Prérequis

- Docker 20.10+
- Docker Compose 2.0+

## Démarrage rapide

### Option 1 : Construire localement

```bash
# Cloner le dépôt
git clone https://github.com/duckling-ui/duckling.git
cd duckling

# Construire et démarrer (mode développement)
docker-compose up --build

# Ou exécuter en arrière-plan
docker-compose up -d --build
```

### Option 2 : Utiliser des images préconstruites

```bash
# Télécharger docker-compose.prebuilt.yml
curl -O https://raw.githubusercontent.com/duckling-ui/duckling/main/docker-compose.prebuilt.yml

# Démarrer avec des images préconstruites
docker-compose -f docker-compose.prebuilt.yml up -d
```

Accédez à l’application sur `http://localhost:3000`

## Fichiers Docker Compose

Duckling fournit plusieurs configurations Docker Compose :

| Fichier | Rôle |
|---------|------|
| `docker-compose.yml` | Développement avec builds locaux |
| `docker-compose.prod.yml` | Surcharges production |
| `docker-compose.prebuilt.yml` | Images préconstruites depuis le registre |

### Développement

```bash
docker-compose up --build
```

### Production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Images préconstruites

```bash
# Registre par défaut (davidgs)
docker-compose -f docker-compose.prebuilt.yml up -d

# Registre personnalisé
DOCKER_REGISTRY=ghcr.io/yourusername docker-compose -f docker-compose.prebuilt.yml up -d

# Version spécifique
VERSION=1.0.0 docker-compose -f docker-compose.prebuilt.yml up -d
```

## Construire les images Docker

### Script de build

Utilisez le script de build fourni pour construire facilement les images. Le script construit automatiquement la documentation MkDocs avant les images Docker :

```bash
# Construire les images localement (inclut la doc)
./scripts/docker-build.sh

# Construire et pousser vers Docker Hub
./scripts/docker-build.sh --push

# Construire avec une version précise
./scripts/docker-build.sh --version 1.0.0

# Construire pour plusieurs plateformes (nécessite buildx)
./scripts/docker-build.sh --multi-platform --push

# Pousser vers un registre personnalisé
./scripts/docker-build.sh --push --registry ghcr.io/yourusername

# Ignorer la construction de la doc (utiliser site/ existant)
./scripts/docker-build.sh --skip-docs
```

!!! note "Construction de la documentation"
    Le script de build exécute automatiquement `mkdocs build` pour que la documentation soit disponible dans les conteneurs Docker. Si MkDocs n’est pas installé, il tente `pip install -r backend/requirements.txt` avant la construction. L’image backend n’installe les dépendances qu’à partir de `backend/requirements.txt`.

### Publication automatique (CI/CD)

Lorsqu’une pull request est fusionnée dans `main`, le workflow GitHub Actions [Publish Docker Images](https://github.com/duckling-ui/duckling/actions/workflows/publish-docker.yml) s’exécute automatiquement. Il :

1. Construit des images multi-plateformes (linux/amd64, linux/arm64)
2. Pousse vers **Docker Hub** en `{DOCKERHUB_USERNAME}/duckling-backend` et `{DOCKERHUB_USERNAME}/duckling-frontend`
3. Pousse vers **GitHub Container Registry** en `ghcr.io/{owner}/duckling-backend` et `ghcr.io/{owner}/duckling-frontend`

Les images sont étiquetées avec la version de `frontend/package.json` et `latest`.

**Secrets du dépôt requis** (Settings → Secrets and variables → Actions) :

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Nom d’utilisateur Docker Hub |
| `DOCKERHUB_TOKEN` | Jeton d’accès Docker Hub (ou mot de passe) |

L’authentification GHCR utilise `GITHUB_TOKEN`, fourni automatiquement par GitHub Actions.

### Build manuel

```bash
# Backend (cible production)
cd backend
docker build --target production -t duckling-backend:latest .

# Frontend
cd frontend
docker build --target production -t duckling-frontend:latest .
```

## Variables d’environnement

Créez un fichier `.env` à la racine du projet :

```env
# Sécurité (requis en production)
SECRET_KEY=your-very-secure-random-key-at-least-32-chars

# Configuration Flask
FLASK_ENV=production
DEBUG=False

# Facultatif : registre personnalisé pour images préconstruites
DOCKER_REGISTRY=davidgs
VERSION=latest
```

!!! warning "Sécurité"
    Définissez toujours une `SECRET_KEY` forte en production. Générez-en une avec :
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

## Gérer les conteneurs

### Voir l’état

```bash
# État des conteneurs
docker-compose ps

# Utilisation des ressources
docker stats
```

### Voir les journaux

```bash
# Tous les services
docker-compose logs -f

# Service précis
docker-compose logs -f backend

# 100 dernières lignes
docker-compose logs --tail=100 backend
```

### Arrêter les services

```bash
# Arrêter les conteneurs
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Arrêter et supprimer les images
docker-compose down --rmi all
```

### Redémarrer les services

```bash
# Tout redémarrer
docker-compose restart

# Redémarrer un service précis
docker-compose restart backend
```

## Prise en charge GPU

Pour l’OCR accéléré par GPU avec des GPU NVIDIA :

```yaml
# docker-compose.gpu.yml
version: '3.8'

services:
  backend:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

Exécution :

```bash
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up
```

!!! note "NVIDIA Container Toolkit"
    La prise en charge GPU nécessite le [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

## Stockage persistant

### Par défaut (montages liés)

```yaml
volumes:
  - ./uploads:/app/uploads
  - ./outputs:/app/outputs
```

### Volumes nommés (recommandé en production)

```yaml
services:
  backend:
    volumes:
      - duckling-uploads:/app/uploads
      - duckling-outputs:/app/outputs
      - duckling-data:/app/data

volumes:
  duckling-uploads:
  duckling-outputs:
  duckling-data:
```

### Sauvegarder les données

```bash
# Sauvegarder les volumes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar cvf /backup/outputs-backup.tar /data

# Restaurer les volumes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar xvf /backup/outputs-backup.tar -C /
```

## Vérifications d’intégrité (health checks)

Les deux conteneurs incluent des health checks :

```bash
# Vérifier le backend
curl http://localhost:5001/api/health
# Réponse : {"status": "healthy", "service": "duckling-backend"}

# Vérifier le frontend (renvoie du HTML)
curl -I http://localhost:3000
# Réponse : HTTP/1.1 200 OK
```

Docker Compose attend les health checks :

```yaml
frontend:
  depends_on:
    backend:
      condition: service_healthy
```

## Limites de ressources

La configuration de production inclut des limites de ressources :

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G

  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

## Réseau

Les services communiquent sur un réseau bridge :

```yaml
networks:
  duckling-network:
    driver: bridge
```

Le frontend proxifie les requêtes API vers le backend :

```
Navigateur → Frontend (nginx:3000) → Backend (flask:5001)
```

## Dépannage

### Le conteneur ne démarre pas

```bash
# Consulter les journaux
docker-compose logs backend

# Vérifier l’état des conteneurs
docker-compose ps

# Inspecter le conteneur
docker inspect duckling-backend
```

### Conflits de ports

Modifiez les ports dans `docker-compose.yml` :

```yaml
services:
  backend:
    ports:
      - "5002:5001"  # Port externe modifié
  frontend:
    ports:
      - "8080:3000"  # Port externe modifié
```

### Échecs de build

```bash
# Vider le cache de build
docker builder prune

# Reconstruire sans cache
docker-compose build --no-cache
```

### Problèmes de mémoire

```bash
# Vérifier l’utilisation mémoire
docker stats

# Augmenter la limite mémoire Docker (Docker Desktop)
# Settings → Resources → Memory
```

### Problèmes réseau

```bash
# Lister les réseaux
docker network ls

# Inspecter le réseau
docker network inspect duckling_duckling-network

# Recréer le réseau
docker-compose down
docker network prune
docker-compose up
```

## Étapes suivantes

- [Déploiement production](../deployment/production.md) – Configuration prête pour la production
- [Montée en charge](../deployment/scaling.md) – Adapter au trafic élevé
- [Sécurité](../deployment/security.md) – Bonnes pratiques de sécurité

