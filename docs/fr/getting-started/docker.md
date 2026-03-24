# Déploiement Docker

Déployez Duckling avec Docker pour une configuration rapide et une isolation.

!!! success "TL;DR - Démarrage en une commete"
    ```bash
    curl -O https://raw.githubusercontent.com/davidgs/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Puis ouvrez `http://localhost:3000` 🎉

## Prérequis

- Docker 20.10+
- Docker Compose 2.0+

## Démarrage rapide

### Option 1: Build Locally

```bash
# Clone the repository
git clone https://github.com/davidgs/duckling.git
cd duckling

# Build and start (development mode)
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Option 2: Use Pre-built Images

```bash
# Download docker-compose.prebuilt.yml
curl -O https://raw.githubusercontent.com/davidgs/duckling/main/docker-compose.prebuilt.yml

# Start with pre-built images
docker-compose -f docker-compose.prebuilt.yml up -d
```

Accédez à l'application à `http://localhost:3000`

## Fichiers Docker Compose

Duckling provides several Docker Compose configurations:

| Fichier | Objectif |
|------|---------|
| `docker-compose.yml` | Développement avec builds locaux |
| `docker-compose.prod.yml` | Surcharges de production |
| `docker-compose.prebuilt.yml` | Images préconstruites du registre |

### Développement

```bash
docker-compose up --build
```

### Production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Pre-built Images

```bash
# Using default registry (davidgs)
docker-compose -f docker-compose.prebuilt.yml up -d

# Using custom registry
DOCKER_REGISTRY=ghcr.io/yourusername docker-compose -f docker-compose.prebuilt.yml up -d

# Using specific version
VERSION=1.0.0 docker-compose -f docker-compose.prebuilt.yml up -d
```

## Construire les images Docker

### Script de construction

Utilisez le script de construction fourni pour une construction d'images facile. Le script construit automatiquement la documentation MkDocs avant de construire les images Docker :

```bash
# Build images locally (includes documentation build)
./scripts/docker-build.sh

# Build and push to Docker Hub
./scripts/docker-build.sh --push

# Build with specific version
./scripts/docker-build.sh --version 1.0.0

# Build for multiple platforms (requires buildx)
./scripts/docker-build.sh --multi-platform --push

# Push to custom registry
./scripts/docker-build.sh --push --registry ghcr.io/yourusername

# Skip documentation build (use existing site/)
./scripts/docker-build.sh --skip-docs
```

!!! note "Construction de la documentation"
    Le script exécute `mkdocs build` pour la documentation dans les conteneurs. Si MkDocs est absent, il tente une installation depuis `requirements-docs.txt` à la racine du dépôt. L'image backend installe MkDocs uniquement via `backend/requirements.txt`.

### Publication automatique (CI/CD)

Lorsqu'une pull request est fusionnée dans `main`, the [Publish Docker Images](https://github.com/davidgs/duckling/actions/workflows/publish-docker.yml) workflow automatically:

1. Construit des images multi-plateformes (linux/amd64, linux/arm64)
2. Pousse vers **Docker Hub** comme `{DOCKERHUB_USERNAME}/duckling-backend` et `{DOCKERHUB_USERNAME}/duckling-frontend`
3. Pousse vers **GitHub Container Registry** comme `ghcr.io/{owner}/duckling-backend` et `ghcr.io/{owner}/duckling-frontend`

Les images sont étiquetées avec la version de `frontend/package.json` et `latest`.

**Secrets de dépôt requis** (Paramètres → Secrets et variables → Actions):

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Nom d'utilisateur Docker Hub |
| `DOCKERHUB_TOKEN` | Jeton d'accès Docker Hub (ou mot de passe) |

L'authentification GHCR utilise `GITHUB_TOKEN`, que GitHub Actions fournit automatiquement.

### Construction manuelle

```bash
# Backend (production target)
cd backend
docker build --target production -t duckling-backend:latest .

# Frontend
cd frontend
docker build --target production -t duckling-frontend:latest .
```

## Variables d'environnement

Créez un `.env` fichier à la racine du projet :

```env
# Security (required for production)
SECRET_KEY=your-very-secure-random-key-at-least-32-chars

# Flask configuration
FLASK_ENV=production
DEBUG=False

# Optional: Custom registry for pre-built images
DOCKER_REGISTRY=davidgs
VERSION=latest
```

!!! warning "Sécurité"
    Définissez toujours une `SECRET_KEY` en production. Générez-en un avec :
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

## Gérer les conteneurs

### Voir le statut

```bash
# Container status
docker-compose ps

# Resource usage
docker stats
```

### Voir les journaux

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Arrêter les services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### Redémarrer les services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

## Support GPU

Pour l'OCR accéléré par GPU avec des GPU NVIDIA :

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

Run with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up
```

!!! note "NVIDIA Container Toolkit"
    Le support GPU nécessite le [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

## Stockage persistant

### Par défaut (Bind Mounts)

```yaml
volumes:
  - ./uploads:/app/uploads
  - ./outputs:/app/outputs
```

### Volumes nommés (recommeté pour la production)

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
# Backup volumes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar cvf /backup/outputs-backup.tar /data

# Restore volumes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar xvf /backup/outputs-backup.tar -C /
```

## Contrôles de santé

Les deux conteneurs incluent des contrôles de santé :

```bash
# Check backend health
curl http://localhost:5001/api/health
# Response: {"status": "healthy", "service": "duckling-backend"}

# Check frontend (returns HTML)
curl -I http://localhost:3000
# Response: HTTP/1.1 200 OK
```

Docker Compose attend les contrôles de santé :

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

Les services communiquent via un réseau bridge :

```yaml
networks:
  duckling-network:
    driver: bridge
```

Le frontend fait proxy des requêtes API vers le backend :

```
Browser → Frontend (nginx:3000) → Backend (flask:5001)
```

## Dépannage

### Le conteneur ne démarre pas

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Inspect container
docker inspect duckling-backend
```

### Conflits de ports

Changer les ports dans `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "5002:5001"  # Change external port
  frontend:
    ports:
      - "8080:3000"  # Change external port
```

### Échecs de construction

```bash
# Clean build cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache
```

### Problèmes de mémoire

```bash
# Check memory usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory
```

### Problèmes de réseau

```bash
# List networks
docker network ls

# Inspect network
docker network inspect duckling_duckling-network

# Recreate network
docker-compose down
docker network prune
docker-compose up
```

## Prochaines étapes

- [Production Déploiement](../deployment/production.md) - Production-ready setup
- [Mise à l'échelle](../deployment/scaling.md) - Échelle for high traffic
- [Sécurité](../deployment/security.md) - Sécurité best practices
