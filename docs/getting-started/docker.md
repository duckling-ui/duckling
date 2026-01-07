# Docker Deployment

Deploy Duckling using Docker for quick setup and isolation.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

## Quick Start

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d --build
```

Access the application at `http://localhost:3000`

## Docker Compose Configuration

The default `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5001:5001"
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY:-change-me-in-production}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-very-secure-random-key
FLASK_ENV=production
```

## Managing Containers

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Stop Services

```bash
docker-compose down
```

### Rebuild After Changes

```bash
docker-compose up --build
```

## Building Individual Images

### Backend

```bash
cd backend
docker build -t duckling-backend .
docker run -p 5001:5001 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  duckling-backend
```

### Frontend

```bash
cd frontend
docker build -t duckling-frontend .
docker run -p 3000:80 duckling-frontend
```

## GPU Support

For GPU-accelerated OCR:

```yaml
# docker-compose.gpu.yml
services:
  backend:
    build: ./backend
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

## Persistent Storage

The default configuration mounts:

- `./uploads` - Temporary file uploads
- `./outputs` - Converted documents

To use named volumes:

```yaml
services:
  backend:
    volumes:
      - uploads:/app/uploads
      - outputs:/app/outputs

volumes:
  uploads:
  outputs:
```

## Health Checks

Check service health:

```bash
# Backend health
curl http://localhost:5001/api/health

# Response
{"status": "healthy", "service": "duckling-backend"}
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps
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
      - "8080:80"    # Change external port
```

### Memory Issues

Limit container memory:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G
```

## Next Steps

- [Production Deployment](../deployment/production.md) - Production-ready setup
- [Scaling](../deployment/scaling.md) - Scale for high traffic

