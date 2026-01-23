# Docker Deployment

Deploy Duckling using Docker for quick setup and isolation.

!!! success "TL;DR - One Command Start"
    ```bash
    curl -O https://raw.githubusercontent.com/davidgs/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Then open `http://localhost:3000` 🎉

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

## Quick Start

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

Access the application at `http://localhost:3000`

## Docker Compose Files

Duckling provides several Docker Compose configurations:

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Development with local builds |
| `docker-compose.prod.yml` | Production overrides |
| `docker-compose.prebuilt.yml` | Pre-built images from registry |

### Development

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

## Building Docker Images

### Build Script

Use the provided build script for easy image building. The script automatically builds the MkDocs documentation before building Docker images:

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

!!! note "Documentation Build"
    The build script automatically runs `mkdocs build` to ensure documentation is available in the Docker containers. If MkDocs is not installed, it will attempt to install it from `requirements-docs.txt`.

### Manual Build

```bash
# Backend (production target)
cd backend
docker build --target production -t duckling-backend:latest .

# Frontend
cd frontend
docker build --target production -t duckling-frontend:latest .
```

## Environment Variables

Create a `.env` file in the project root:

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

!!! warning "Security"
    Always set a strong `SECRET_KEY` in production. Generate one with:
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

## Managing Containers

### View Status

```bash
# Container status
docker-compose ps

# Resource usage
docker stats
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Stop Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

## GPU Support

For GPU-accelerated OCR with NVIDIA GPUs:

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
    GPU support requires the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

## Persistent Storage

### Default (Bind Mounts)

```yaml
volumes:
  - ./uploads:/app/uploads
  - ./outputs:/app/outputs
```

### Named Volumes (Recommended for Production)

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

### Backup Data

```bash
# Backup volumes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar cvf /backup/outputs-backup.tar /data

# Restore volumes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar xvf /backup/outputs-backup.tar -C /
```

## Health Checks

Both containers include health checks:

```bash
# Check backend health
curl http://localhost:5001/api/health
# Response: {"status": "healthy", "service": "duckling-backend"}

# Check frontend (returns HTML)
curl -I http://localhost:3000
# Response: HTTP/1.1 200 OK
```

Docker Compose waits for health checks:

```yaml
frontend:
  depends_on:
    backend:
      condition: service_healthy
```

## Resource Limits

Production configuration includes resource limits:

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

## Networking

Services communicate over a bridge network:

```yaml
networks:
  duckling-network:
    driver: bridge
```

The frontend proxies API requests to the backend:

```
Browser → Frontend (nginx:3000) → Backend (flask:5001)
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Inspect container
docker inspect duckling-backend
```

### Port Conflicts

Change ports in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "5002:5001"  # Change external port
  frontend:
    ports:
      - "8080:3000"  # Change external port
```

### Build Failures

```bash
# Clean build cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache
```

### Memory Issues

```bash
# Check memory usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory
```

### Network Issues

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

## Next Steps

- [Production Deployment](../deployment/production.md) - Production-ready setup
- [Scaling](../deployment/scaling.md) - Scale for high traffic
- [Security](../deployment/security.md) - Security best practices
