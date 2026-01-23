# Scaling

Guide for scaling Duckling for high-traffic deployments.

## Architecture for Scale

```mermaid
graph LR
    LB[Load Balancer]

    LB --> B1[Backend 1]
    LB --> B2[Backend 2]
    LB --> B3[Backend 3]

    B1 --> Redis[(Redis Queue)]
    B2 --> Redis
    B3 --> Redis

    B1 --> PG[(PostgreSQL)]
    B2 --> PG
    B3 --> PG

    B1 --> S3[(S3 Storage)]
    B2 --> S3
    B3 --> S3

    style LB fill:#f59e0b,color:#fff
    style Redis fill:#dc2626,color:#fff
    style PG fill:#3b82f6,color:#fff
    style S3 fill:#22c55e,color:#fff
```

## Horizontal Scaling

For high-traffic deployments:

1. **Load Balancer**: Use nginx, HAProxy, or cloud LB
2. **Multiple Backend Instances**: Run multiple Gunicorn processes
3. **Shared Storage**: Use NFS or object storage for uploads/outputs
4. **Database**: Consider PostgreSQL for history (instead of SQLite)

---

## Resource Requirements

| Deployment | CPU | RAM | Storage |
|------------|-----|-----|---------|
| Development | 2 cores | 4GB | 10GB |
| Small (< 100 docs/day) | 4 cores | 8GB | 50GB |
| Medium (< 1000 docs/day) | 8 cores | 16GB | 200GB |
| Large (> 1000 docs/day) | 16+ cores | 32GB+ | 500GB+ |

---

## Load Balancing with Nginx

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

        # Sticky sessions for job polling
        ip_hash;
    }
}
```

---

## Redis Job Queue

For production with multiple workers, replace the threading-based queue with Redis:

### Installation

```bash
pip install celery redis
```

### Configuration

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
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,
)
```

### Task Definition

```python
@celery.task(bind=True)
def convert_document(self, job_id: str, file_path: str, settings: dict):
    """Convert a document asynchronously."""
    try:
        result = converter_service.convert(file_path, settings)
        return {'job_id': job_id, 'status': 'completed', 'result': result}
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
```

### Running Workers

```bash
celery -A celery_config worker --loglevel=info --concurrency=4
```

---

## PostgreSQL Migration

For multi-instance deployments, migrate from SQLite to PostgreSQL:

### Configuration

```python
# config.py
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/docling'
)
```

### Migration Script

```python
# migrate_to_postgres.py
import sqlite3
import psycopg2

def migrate():
    sqlite_conn = sqlite3.connect('history.db')
    pg_conn = psycopg2.connect(DATABASE_URL)

    # Copy data from SQLite to PostgreSQL
    # ...
```

---

## Object Storage (S3)

Use S3 or compatible storage for uploads and outputs:

### Configuration

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

### File Operations

```python
def upload_to_s3(file_path: str, key: str):
    s3.upload_file(file_path, BUCKET_NAME, key)

def download_from_s3(key: str, file_path: str):
    s3.download_file(BUCKET_NAME, key, file_path)
```

---

## GPU Acceleration

For high-volume OCR processing:

### Docker with GPU

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

### Kubernetes with GPU

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

## Monitoring

### Prometheus Metrics

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Custom metrics
conversion_counter = metrics.counter(
    'conversions_total',
    'Total conversions',
    labels={'status': lambda: 'success'}
)
```

### Grafana Dashboard

Key metrics to monitor:

- Conversion rate (documents/minute)
- Queue depth
- Processing time (p50, p95, p99)
- Error rate
- Memory usage
- CPU utilization

---

## Kubernetes Deployment

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

