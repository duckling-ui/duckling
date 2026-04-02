# Docker-Bereitstellung

Stellen Sie Duckling mit Docker für schnelle Einrichtung und Isolation bereit.

!!! success "TL;DR - Ein-Befehl-Start"
    ```bash
    curl -O https://raw.githubusercontent.com/davidgs/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Dann öffnen Sie `http://localhost:3000` 🎉

## Voraussetzungen

- Docker 20.10+
- Docker Compose 2.0+

## Schnellstart

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

Greifen Sie auf die Anwendung unter zu `http://localhost:3000`

## Docker Compose-Dateien

Duckling provides several Docker Compose configurations:

| Datei | Zweck |
|------|---------|
| `docker-compose.yml` | Entwicklung mit lokalen Builds |
| `docker-compose.prod.yml` | Produktionsüberschreibungen |
| `docker-compose.prebuilt.yml` | Vorgefertigte Images aus der Registry |

### Entwicklung

```bash
docker-compose up --build
```

### Produktion

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

## Docker-Images erstellen

### Build-Skript

Verwenden Sie das bereitgestellte Build-Skript für einfaches Image-Building. Das Skript erstellt automatisch die MkDocs-Dokumentation vor dem Erstellen der Docker-Images:

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

!!! note "Dokumentations-Build"
    Das Skript führt `mkdocs build` für die Dokumentation in den Containern aus. Fehlt MkDocs, wird `pip install -r backend/requirements.txt` versucht. Das Backend-Image installiert Abhängigkeiten nur über `backend/requirements.txt`.

### Automatische Veröffentlichung (CI/CD)

Wenn ein Pull Request in `main`, the [Publish Docker Images](https://github.com/davidgs/duckling/actions/workflows/publish-docker.yml) workflow automatically:

1. Erstellt Multi-Platform-Images (linux/amd64, linux/arm64)
2. Pusht zu **Docker Hub** als `{DOCKERHUB_USERNAME}/duckling-backend` und `{DOCKERHUB_USERNAME}/duckling-frontend`
3. Pusht zu **GitHub Container Registry** als `ghcr.io/{owner}/duckling-backend` und `ghcr.io/{owner}/duckling-frontend`

Images werden mit der Version aus getaggt `frontend/package.json` und `latest`.

**Erforderliche Repository-Geheimnisse** (Einstellungen → Geheimniss und variables → Actions):

| Geheimnis | Beschreibung |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Docker Hub-Benutzername |
| `DOCKERHUB_TOKEN` | Docker Hub-Zugriffstoken (oder Passwort) |

GHCR-Authentifizierung verwendet `GITHUB_TOKEN`, das GitHub Actions automatisch bereitstellt.

### Manueller Build

```bash
# Backend (production target)
cd backend
docker build --target production -t duckling-backend:latest .

# Frontend
cd frontend
docker build --target production -t duckling-frontend:latest .
```

## Umgebungsvariablen

Erstellen Sie eine `.env` Datei im Projektstamm:

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

!!! warning "Sicherheit"
    Setzenzen Sie immer einen starken `SECRET_KEY` in der Produktion. Erzeugen Sie einen mit:
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

## Container verwalten

### Status anzeigen

```bash
# Container status
docker-compose ps

# Resource usage
docker stats
```

### Protokolle anzeigen

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Dienste stoppen

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### Dienste neu starten

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

## GPU-Unterstützung

Für GPU-beschleunigtes OCR mit NVIDIA-GPUs:

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
    GPU-Unterstützung erfordert das [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

## Persistenter Speicher

### Stundard (Bind Mounts)

```yaml
volumes:
  - ./uploads:/app/uploads
  - ./outputs:/app/outputs
```

### Benannte Volumes (empfohlen für Produktion)

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

### Daten sichern

```bash
# Backup volumes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar cvf /backup/outputs-backup.tar /data

# Restore volumes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar xvf /backup/outputs-backup.tar -C /
```

## Health-Checks

Beide Container enthalten Health-Checks:

```bash
# Check backend health
curl http://localhost:5001/api/health
# Response: {"status": "healthy", "service": "duckling-backend"}

# Check frontend (returns HTML)
curl -I http://localhost:3000
# Response: HTTP/1.1 200 OK
```

Docker Compose wartet auf Health-Checks:

```yaml
frontend:
  depends_on:
    backend:
      condition: service_healthy
```

## Ressourcenlimits

Die Produktionskonfiguration enthält Ressourcenlimits:

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

## Netzwerk

Dienste kommunizieren über ein Bridge-Netzwerk:

```yaml
networks:
  duckling-network:
    driver: bridge
```

Das Frontend leitet API-Anfragen an das Backend weiter:

```
Browser → Frontend (nginx:3000) → Backend (flask:5001)
```

## Fehlerbehebung

### Container startet nicht

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Inspect container
docker inspect duckling-backend
```

### Portkonflikte

Ports ändern in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "5002:5001"  # Change external port
  frontend:
    ports:
      - "8080:3000"  # Change external port
```

### Build-Fehler

```bash
# Clean build cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache
```

### Speicherprobleme

```bash
# Check memory usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory
```

### Netzwerkprobleme

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

## Nächste Schritte

- [Produktion Bereitstellung](../deployment/production.md) - Produktion-ready setup
- [Skalierung](../deployment/scaling.md) - Skalierung for high traffic
- [Sicherheit](../deployment/security.md) - Sicherheit best practices
