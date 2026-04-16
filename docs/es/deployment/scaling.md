# Escalado

Guía para escalar Duckling en despliegues de alto tráfico.

## Arquitectura para escalar

```mermaid
graph LR
    LB[Balanceador de carga]

    LB --> B1[Backend 1]
    LB --> B2[Backend 2]
    LB --> B3[Backend 3]

    B1 --> Redis[(Cola Redis)]
    B2 --> Redis
    B3 --> Redis

    B1 --> PG[(PostgreSQL)]
    B2 --> PG
    B3 --> PG

    B1 --> S3[(Almacenamiento S3)]
    B2 --> S3
    B3 --> S3

    style LB fill:#f59e0b,color:#fff
    style Redis fill:#dc2626,color:#fff
    style PG fill:#3b82f6,color:#fff
    style S3 fill:#22c55e,color:#fff
```

## Escalado horizontal

Para despliegues de alto tráfico:

1. **Balanceador de carga**: use nginx, HAProxy o un balanceador en la nube
2. **Varias instancias de backend**: ejecute varios procesos Gunicorn
3. **Almacenamiento compartido**: NFS o almacenamiento de objetos para subidas y salidas
4. **Base de datos**: considere PostgreSQL para el historial (en lugar de SQLite)

---

## Requisitos de recursos

| Despliegue | CPU | RAM | Almacenamiento |
|------------|-----|-----|---------|
| Desarrollo | 2 núcleos | 4 GB | 10 GB |
| Pequeño (< 100 doc./día) | 4 núcleos | 8 GB | 50 GB |
| Medio (< 1000 doc./día) | 8 núcleos | 16 GB | 200 GB |
| Grande (> 1000 doc./día) | 16+ núcleos | 32 GB+ | 500 GB+ |

---

## Balanceo de carga con Nginx

```nginx
upstream docling_backends {
    least_conn;
    server 10.0.0.1:5001 weight=1;
    server 10.0.0.2:5001 weight=1;
    server 10.0.0.3:5001 weight=1;
}

server {
    listen 80;
    server_name docling.example.com;

    location /api/ {
        proxy_pass http://docling_backends;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # Sesiones persistentes para sondeo de trabajos
        ip_hash;
    }
}
```

---

## Cola de trabajos Redis

En producción con varios workers, sustituya la cola basada en hilos por Redis:

### Instalación

```bash
pip install celery redis
```

### Configuración

```python
# celery_config.py
from celery import Celery

celery = Celery(
    'docling',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_time_limit=600,  # 10 minutos
    task_soft_time_limit=540,
)
```

### Definición de tarea

```python
@celery.task(bind=True)
def convert_document(self, job_id: str, file_path: str, settings: dict):
    """Convertir un documento de forma asíncrona."""
    try:
        result = converter_service.convert(file_path, settings)
        return {'job_id': job_id, 'status': 'completed', 'result': result}
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
```

### Ejecución de workers

```bash
celery -A celery_config worker --loglevel=info --concurrency=4
```

---

## Migración a PostgreSQL

En despliegues con varias instancias, migre de SQLite a PostgreSQL:

### Configuración

```python
# config.py
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/docling'
)
```

### Script de migración

```python
# migrate_to_postgres.py
import sqlite3
import psycopg2

def migrate():
    sqlite_conn = sqlite3.connect('history.db')
    pg_conn = psycopg2.connect(DATABASE_URL)

    # Copiar datos de SQLite a PostgreSQL
    # ...
```

---

## Almacenamiento de objetos (S3)

Use S3 o almacenamiento compatible para subidas y salidas:

### Configuración

```python
import boto3

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name='us-east-1'
)

BUCKET_NAME = 'duckling-files'
```

### Operaciones con archivos

```python
def upload_to_s3(file_path: str, key: str):
    s3.upload_file(file_path, BUCKET_NAME, key)

def download_from_s3(key: str, file_path: str):
    s3.download_file(BUCKET_NAME, key, file_path)
```

---

## Aceleración por GPU

Para un volumen alto de OCR:

### Docker con GPU

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

### Kubernetes con GPU

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-backend
spec:
  template:
    spec:
      containers:
        - name: backend
          resources:
            limits:
              nvidia.com/gpu: 1
```

---

## Monitorización

### Métricas de Prometheus

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Métricas personalizadas
conversion_counter = metrics.counter(
    'conversions_total',
    'Total de conversiones',
    labels={'status': lambda: 'success'}
)
```

### Panel de Grafana

Métricas clave:

- Tasa de conversión (documentos/minuto)
- Profundidad de cola
- Tiempo de procesamiento (p50, p95, p99)
- Tasa de error
- Uso de memoria
- Uso de CPU

---

## Despliegue en Kubernetes

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: docling-backend
  template:
    metadata:
      labels:
        app: docling-backend
    spec:
      containers:
        - name: backend
          image: duckling-backend:latest
          ports:
            - containerPort: 5001
          resources:
            requests:
              memory: "2Gi"
              cpu: "500m"
            limits:
              memory: "4Gi"
              cpu: "2000m"
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: docling-secrets
                  key: database-url
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: docling-backend
spec:
  selector:
    app: docling-backend
  ports:
    - port: 5001
      targetPort: 5001
  type: ClusterIP
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: docling-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: docling-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

