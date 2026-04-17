# Docker-Bereitstellung

Stellen Sie Duckling mit Docker für schnelles Setup und Isolation bereit.

!!! success "Kurz gefasst – Start mit einem Befehl"
    ```bash
    curl -O https://raw.githubusercontent.com/duckling-ui/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Öffnen Sie anschließend `http://localhost:3000` 🎉

## Voraussetzungen

- Docker 20.10+
- Docker Compose 2.0+

## Schnellstart

### Option 1: Lokal bauen

```bash
# Clone the repository
git clone https://github.com/duckling-ui/duckling.git
cd duckling

# Bauen und starten (Entwicklungsmodus)
docker-compose up --build

# Oder im Hintergrund ausführen
docker-compose up -d --build
```

### Option 2: Vorgefertigte Images nutzen

```bash
# Download docker-compose.prebuilt.yml
curl -O https://raw.githubusercontent.com/duckling-ui/duckling/main/docker-compose.prebuilt.yml

# Mit vorgefertigten Images starten
docker-compose -f docker-compose.prebuilt.yml up -d
```

Die Anwendung erreichen Sie unter `http://localhost:3000`

## Docker-Compose-Dateien

Duckling stellt mehrere Docker-Compose-Konfigurationen bereit:

| Datei | Zweck |
|-------|--------|
| `docker-compose.yml` | Entwicklung mit lokalem Build |
| `docker-compose.prod.yml` | Produktions-Overrides |
| `docker-compose.prebuilt.yml` | Vorgefertigte Images aus der Registry |

### Entwicklung

```bash
docker-compose up --build
```

### Produktion

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Vorgefertigte Images

```bash
# Standard-Registry (ducklingui)
docker-compose -f docker-compose.prebuilt.yml up -d

# Eigene Registry
DOCKER_REGISTRY=ghcr.io/yourusername docker-compose -f docker-compose.prebuilt.yml up -d

# Bestimmte Version
VERSION=1.0.0 docker-compose -f docker-compose.prebuilt.yml up -d
```

## Docker-Images bauen

### Build-Skript

Nutzen Sie das mitgelieferte Build-Skript zum einfachen Erstellen von Images. Das Skript baut die MkDocs-Dokumentation automatisch, bevor die Docker-Images gebaut werden:

```bash
# Images lokal bauen (inkl. Dokumentations-Build)
./scripts/docker-build.sh

# Bauen und nach Docker Hub pushen
./scripts/docker-build.sh --push

# Mit bestimmter Version bauen
./scripts/docker-build.sh --version 1.0.0

# Für mehrere Plattformen (erfordert buildx)
./scripts/docker-build.sh --multi-platform --push

# Zu eigener Registry pushen
./scripts/docker-build.sh --push --registry ghcr.io/yourusername

# Dokumentations-Build überspringen (vorhandenes site/ nutzen)
./scripts/docker-build.sh --skip-docs
```

!!! note "Dokumentations-Build"
    Das Build-Skript führt automatisch `mkdocs build` aus, damit die Dokumentation in den Docker-Containern verfügbar ist. Ist MkDocs nicht installiert, versucht es `pip install -r backend/requirements.txt` vor dem Build. Das Backend-Image installiert Abhängigkeiten nur aus `backend/requirements.txt`.

### Automatisches Veröffentlichen (CI/CD)

Wenn ein Pull Request in `main` gemergt wird, läuft der [Publish Docker Images](https://github.com/duckling-ui/duckling/actions/workflows/publish-docker.yml)-GitHub-Actions-Workflow automatisch. Er:

1. Baut Multiplattform-Images (linux/amd64, linux/arm64)
2. Pusht zu **Docker Hub** als `{DOCKERHUB_USERNAME}/duckling-backend` und `{DOCKERHUB_USERNAME}/duckling-frontend`
3. Pusht zu **GitHub Container Registry** als `ghcr.io/{owner}/duckling-backend` und `ghcr.io/{owner}/duckling-frontend`

Images werden mit der Version aus `frontend/package.json` und `latest` getaggt.

**Erforderliche Repository-Geheimnisse** (Einstellungen → Secrets and variables → Actions):

| Geheimnis | Beschreibung |
|-----------|--------------|
| `DOCKERHUB_USERNAME` | Docker-Hub-Benutzername |
| `DOCKERHUB_TOKEN` | Docker-Hub-Zugangstoken (oder Passwort) |

Die GHCR-Authentifizierung nutzt `GITHUB_TOKEN`, das GitHub Actions automatisch bereitstellt.

### Manueller Build

```bash
# Backend (Production-Target)
cd backend
docker build --target production -t duckling-backend:latest .

# Frontend
cd frontend
docker build --target production -t duckling-frontend:latest .
```

## Umgebungsvariablen

Legen Sie eine `.env`-Datei im Stammverzeichnis des Projekts an:

```env
# Sicherheit (in Produktion erforderlich)
SECRET_KEY=your-very-secure-random-key-at-least-32-chars

# Flask-Konfiguration
FLASK_ENV=production
DEBUG=False

# Optional: Eigene Registry für vorgefertigte Images
DOCKER_REGISTRY=ducklingui
VERSION=latest
```

!!! warning "Sicherheit"
    Setzen Sie in Produktion immer einen starken `SECRET_KEY`. Erzeugen Sie einen mit:
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

## Container verwalten

### Status anzeigen

```bash
# Container-Status
docker-compose ps

# Ressourcennutzung
docker stats
```

### Logs anzeigen

```bash
# Alle Dienste
docker-compose logs -f

# Bestimmter Dienst
docker-compose logs -f backend

# Letzte 100 Zeilen
docker-compose logs --tail=100 backend
```

### Dienste stoppen

```bash
# Container stoppen
docker-compose down

# Stoppen und Volumes entfernen
docker-compose down -v

# Stoppen und Images entfernen
docker-compose down --rmi all
```

### Dienste neu starten

```bash
# Alle neu starten
docker-compose restart

# Bestimmten Dienst neu starten
docker-compose restart backend
```

## GPU-Unterstützung

Für GPU-beschleunigte OCR mit NVIDIA-GPUs:

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

Ausführen mit:

```bash
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up
```

!!! note "NVIDIA Container Toolkit"
    GPU-Unterstützung erfordert das [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

## Persistenter Speicher

### Standard (Bind-Mounts)

```yaml
volumes:
  - ./uploads:/app/uploads
  - ./outputs:/app/outputs
```

### Benannte Volumes (in Produktion empfohlen)

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
# Volumes sichern
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar cvf /backup/outputs-backup.tar /data

# Volumes wiederherstellen
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar xvf /backup/outputs-backup.tar -C /
```

## Health Checks

Beide Container enthalten Health Checks:

```bash
# Backend-Gesundheit prüfen
curl http://localhost:5001/api/health
# Antwort: {"status": "healthy", "service": "duckling-backend"}

# Frontend prüfen (liefert HTML)
curl -I http://localhost:3000
# Antwort: HTTP/1.1 200 OK
```

Docker Compose wartet auf Health Checks:

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

Die Dienste kommunizieren über ein Bridge-Netzwerk:

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
# Logs prüfen
docker-compose logs backend

# Container-Status prüfen
docker-compose ps

# Container inspizieren
docker inspect duckling-backend
```

### Portkonflikte

Ports in `docker-compose.yml` ändern:

```yaml
services:
  backend:
    ports:
      - "5002:5001"  # Externen Port ändern
  frontend:
    ports:
      - "8080:3000"  # Externen Port ändern
```

### Build-Fehler

```bash
# Build-Cache leeren
docker builder prune

# Ohne Cache neu bauen
docker-compose build --no-cache
```

### Speicherprobleme

```bash
# Speichernutzung prüfen
docker stats

# Docker-Speicherlimit erhöhen (Docker Desktop)
# Einstellungen → Resources → Memory
```

### Netzwerkprobleme

```bash
# Netzwerke auflisten
docker network ls

# Netzwerk inspizieren
docker network inspect duckling_duckling-network

# Netzwerk neu erstellen
docker-compose down
docker network prune
docker-compose up
```

## Nächste Schritte

- [Produktionsbereitstellung](../deployment/production.md) – Setup für Produktion
- [Skalierung](../deployment/scaling.md) – Für hohen Traffic skalieren
- [Sicherheit](../deployment/security.md) – Sicherheits-Best Practices

