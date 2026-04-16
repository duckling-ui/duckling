# Despliegue con Docker

Despliegue Duckling con Docker para una puesta en marcha rápida y aislamiento.

!!! success "Resumen – Inicio con un comando"
    ```bash
    curl -O https://raw.githubusercontent.com/duckling-ui/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Luego abra `http://localhost:3000` 🎉

## Requisitos previos

- Docker 20.10+
- Docker Compose 2.0+

## Inicio rápido

### Opción 1: Compilar localmente

```bash
# Clonar el repositorio
git clone https://github.com/duckling-ui/duckling.git
cd duckling

# Compilar e iniciar (modo desarrollo)
docker-compose up --build

# O ejecutar en segundo plano
docker-compose up -d --build
```

### Opción 2: Usar imágenes precompiladas

```bash
# Descargar docker-compose.prebuilt.yml
curl -O https://raw.githubusercontent.com/duckling-ui/duckling/main/docker-compose.prebuilt.yml

# Iniciar con imágenes precompiladas
docker-compose -f docker-compose.prebuilt.yml up -d
```

Acceda a la aplicación en `http://localhost:3000`

## Archivos de Docker Compose

Duckling ofrece varias configuraciones de Docker Compose:

| Archivo | Propósito |
|---------|-----------|
| `docker-compose.yml` | Desarrollo con compilaciones locales |
| `docker-compose.prod.yml` | Ajustes de producción |
| `docker-compose.prebuilt.yml` | Imágenes precompiladas del registro |

### Desarrollo

```bash
docker-compose up --build
```

### Producción

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Imágenes precompiladas

```bash
# Registro predeterminado (davidgs)
docker-compose -f docker-compose.prebuilt.yml up -d

# Registro personalizado
DOCKER_REGISTRY=ghcr.io/yourusername docker-compose -f docker-compose.prebuilt.yml up -d

# Versión concreta
VERSION=1.0.0 docker-compose -f docker-compose.prebuilt.yml up -d
```

## Compilar imágenes Docker

### Script de compilación

Use el script de compilación incluido para crear imágenes fácilmente. El script compila automáticamente la documentación MkDocs antes de las imágenes Docker:

```bash
# Compilar imágenes localmente (incluye la documentación)
./scripts/docker-build.sh

# Compilar y publicar en Docker Hub
./scripts/docker-build.sh --push

# Compilar con una versión concreta
./scripts/docker-build.sh --version 1.0.0

# Compilar para varias plataformas (requiere buildx)
./scripts/docker-build.sh --multi-platform --push

# Publicar en un registro personalizado
./scripts/docker-build.sh --push --registry ghcr.io/yourusername

# Omitir la compilación de documentación (usar site/ existente)
./scripts/docker-build.sh --skip-docs
```

!!! note "Compilación de la documentación"
    El script de compilación ejecuta automáticamente `mkdocs build` para que la documentación esté disponible en los contenedores Docker. Si MkDocs no está instalado, intenta `pip install -r backend/requirements.txt` antes de compilar. La imagen del backend instala dependencias solo desde `backend/requirements.txt`.

### Publicación automática (CI/CD)

Cuando se fusiona una pull request en `main`, el flujo de trabajo de GitHub Actions [Publish Docker Images](https://github.com/duckling-ui/duckling/actions/workflows/publish-docker.yml) se ejecuta automáticamente. Este flujo:

1. Compila imágenes multiplataforma (linux/amd64, linux/arm64)
2. Publica en **Docker Hub** como `{DOCKERHUB_USERNAME}/duckling-backend` y `{DOCKERHUB_USERNAME}/duckling-frontend`
3. Publica en **GitHub Container Registry** como `ghcr.io/{owner}/duckling-backend` y `ghcr.io/{owner}/duckling-frontend`

Las imágenes se etiquetan con la versión de `frontend/package.json` y `latest`.

**Secretos del repositorio necesarios** (Settings → Secrets and variables → Actions):

| Secreto | Descripción |
|---------|-------------|
| `DOCKERHUB_USERNAME` | Usuario de Docker Hub |
| `DOCKERHUB_TOKEN` | Token de acceso de Docker Hub (o contraseña) |

La autenticación en GHCR usa `GITHUB_TOKEN`, que GitHub Actions proporciona automáticamente.

### Compilación manual

```bash
# Backend (objetivo production)
cd backend
docker build --target production -t duckling-backend:latest .

# Frontend
cd frontend
docker build --target production -t duckling-frontend:latest .
```

## Variables de entorno

Cree un archivo `.env` en la raíz del proyecto:

```env
# Seguridad (obligatorio en producción)
SECRET_KEY=your-very-secure-random-key-at-least-32-chars

# Configuración de Flask
FLASK_ENV=production
DEBUG=False

# Opcional: registro personalizado para imágenes precompiladas
DOCKER_REGISTRY=davidgs
VERSION=latest
```

!!! warning "Seguridad"
    Establezca siempre una `SECRET_KEY` segura en producción. Genérela con:
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

## Gestionar contenedores

### Ver estado

```bash
# Estado de los contenedores
docker-compose ps

# Uso de recursos
docker stats
```

### Ver registros

```bash
# Todos los servicios
docker-compose logs -f

# Servicio concreto
docker-compose logs -f backend

# Últimas 100 líneas
docker-compose logs --tail=100 backend
```

### Detener servicios

```bash
# Detener contenedores
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Detener y eliminar imágenes
docker-compose down --rmi all
```

### Reiniciar servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar un servicio concreto
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

Ejecución:

```bash
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up
```

!!! note "NVIDIA Container Toolkit"
    El soporte GPU requiere el [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

## Almacenamiento persistente

### Predeterminado (montajes enlazados)

```yaml
volumes:
  - ./uploads:/app/uploads
  - ./outputs:/app/outputs
```

### Volúmenes con nombre (recomendado en producción)

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

### Copia de seguridad de datos

```bash
# Respaldar volúmenes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar cvf /backup/outputs-backup.tar /data

# Restaurar volúmenes
docker run --rm -v duckling-outputs:/data -v $(pwd):/backup alpine tar xvf /backup/outputs-backup.tar -C /
```

## Comprobaciones de salud

Ambos contenedores incluyen comprobaciones de salud:

```bash
# Comprobar salud del backend
curl http://localhost:5001/api/health
# Respuesta: {"status": "healthy", "service": "duckling-backend"}

# Comprobar frontend (devuelve HTML)
curl -I http://localhost:3000
# Respuesta: HTTP/1.1 200 OK
```

Docker Compose espera a las comprobaciones de salud:

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

Los servicios se comunican por una red bridge:

```yaml
networks:
  duckling-network:
    driver: bridge
```

El frontend enruta las peticiones API al backend:

```
Navegador → Frontend (nginx:3000) → Backend (flask:5001)
```

## Solución de problemas

### El contenedor no arranca

```bash
# Ver registros
docker-compose logs backend

# Ver estado de contenedores
docker-compose ps

# Inspeccionar contenedor
docker inspect duckling-backend
```

### Conflictos de puertos

Cambie los puertos en `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "5002:5001"  # Cambiar puerto externo
  frontend:
    ports:
      - "8080:3000"  # Cambiar puerto externo
```

### Fallos de compilación

```bash
# Limpiar caché de compilación
docker builder prune

# Recompilar sin caché
docker-compose build --no-cache
```

### Problemas de memoria

```bash
# Ver uso de memoria
docker stats

# Aumentar límite de memoria de Docker (Docker Desktop)
# Settings → Resources → Memory
```

### Problemas de red

```bash
# Listar redes
docker network ls

# Inspeccionar red
docker network inspect duckling_duckling-network

# Recrear red
docker-compose down
docker network prune
docker-compose up
```

## Próximos pasos

- [Despliegue en producción](../deployment/production.md) – Configuración lista para producción
- [Escalado](../deployment/scaling.md) – Escalar para mucho tráfico
- [Seguridad](../deployment/security.md) – Buenas prácticas de seguridad

