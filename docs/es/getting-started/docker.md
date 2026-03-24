# Despliegue con Docker

Despliega Duckling con Docker para una configuración rápida y aislamiento.

!!! success "TL;DR - Inicio con un comyo"
    ```bash
    curl -O https://raw.githubusercontent.com/davidgs/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Luego abre `http://localhost:3000` 🎉

## Requisitos previos

- Docker 20.10+
- Docker Compose 2.0+

## Inicio rápido

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

Accede a la aplicación en `http://localhost:3000`

## Archivos Docker Compose

Duckling provides several Docker Compose configurations:

| Archivo | Propósito |
|------|---------|
| `docker-compose.yml` | Desarrollo con construcciones locales |
| `docker-compose.prod.yml` | Anulaciones de producción |
| `docker-compose.prebuilt.yml` | Imágenes preconstruidas del registro |

### Desarrollo

```bash
docker-compose up --build
```

### Producción

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

## Construir imágenes Docker

### Script de construcción

Usa el script de construcción proporcionado para una fácil construcción de imágenes. El script construye automáticamente la documentación MkDocs antes de construir las imágenes Docker:

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

!!! note "Construcción de documentación"
    El script ejecuta `mkdocs build` para la documentación en los contenedores. Si MkDocs no está instalado, intentará instalarlo desde `requirements-docs.txt` en la raíz del repositorio. La imagen del backend instala MkDocs solo con `backend/requirements.txt`.

### Publicación automática (CI/CD)

Cuyo una solicitud de extracción se fusiona en `main`, the [Publish Docker Images](https://github.com/davidgs/duckling/actions/workflows/publish-docker.yml) workflow automatically:

1. Construye imágenes multiplataforma (linux/amd64, linux/arm64)
2. Sube a **Docker Hub** como `{DOCKERHUB_USERNAME}/duckling-backend` y `{DOCKERHUB_USERNAME}/duckling-frontend`
3. Sube a **GitHub Container Registry** como `ghcr.io/{owner}/duckling-backend` y `ghcr.io/{owner}/duckling-frontend`

Las imágenes se etiquetan con la versión de `frontend/package.json` y `latest`.

**Secretoos de repositorio requeridos** (Configuración → Secretos y variables → Actions):

| Secreto | Descripción |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Nombre de usuario de Docker Hub |
| `DOCKERHUB_TOKEN` | Token de acceso de Docker Hub (o contraseña) |

La autenticación GHCR usa `GITHUB_TOKEN`, que GitHub Actions proporciona automáticamente.

### Construcción manual

```bash
# Backend (production target)
cd backend
docker build --target production -t duckling-backend:latest .

# Frontend
cd frontend
docker build --target production -t duckling-frontend:latest .
```

## Variables de entorno

Crea un `.env` archivo en la raíz del proyecto:

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

!!! warning "Seguridad"
    Siempre establece una `SECRET_KEY` en producción. Genera uno con:
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

## Gestionar contenedores

### Ver estado

```bash
# Container status
docker-compose ps

# Resource usage
docker stats
```

### Ver registros

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Detener servicios

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### Reiniciar servicios

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

## Soporte GPU

Para OCR acelerado por GPU con GPUs NVIDIA:

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
    El soporte GPU requiere el [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

## Almacenamiento persistente

### Predeterminado (Bind Mounts)

```yaml
volumes:
  - ./uploads:/app/uploads
  - ./outputs:/app/outputs
```

### Volúmenes con nombre (recomendado para producción)

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

### Respaldar datos

```bash
# Backup volumes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar cvf /backup/outputs-backup.tar /data

# Restore volumes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar xvf /backup/outputs-backup.tar -C /
```

## Comprobaciones de estado

Ambos contenedores incluyen comprobaciones de estado:

```bash
# Check backend health
curl http://localhost:5001/api/health
# Response: {"status": "healthy", "service": "duckling-backend"}

# Check frontend (returns HTML)
curl -I http://localhost:3000
# Response: HTTP/1.1 200 OK
```

Docker Compose espera las comprobaciones de estado:

```yaml
frontend:
  depends_on:
    backend:
      condition: service_healthy
```

## Límites de recursos

La configuración de producción incluye límites de recursos:

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

## Red

Los servicios se comunican a través de una red puente:

```yaml
networks:
  duckling-network:
    driver: bridge
```

El frontend hace proxy de las solicitudes API al backend:

```
Browser → Frontend (nginx:3000) → Backend (flask:5001)
```

## Solución de problemas

### El contenedor no inicia

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Inspect container
docker inspect duckling-backend
```

### Conflictos de puertos

Cambiar puertos en `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "5002:5001"  # Change external port
  frontend:
    ports:
      - "8080:3000"  # Change external port
```

### Fallos de construcción

```bash
# Clean build cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache
```

### Problemas de memoria

```bash
# Check memory usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory
```

### Problemas de red

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

## Próximos pasos

- [Producción Despliegue](../deployment/production.md) - Producción-ready setup
- [Escalado](../deployment/scaling.md) - Escala for high traffic
- [Seguridad](../deployment/security.md) - Seguridad best practices
