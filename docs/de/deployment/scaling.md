# Skalierung

Anleitung zur Skalierung von Duckling für Deployments mit hohem Traffic.

## Architektur für Skalierung

```mermaid
graph LR
    LB[Lastverteiler]

    LB --> B1[Backend 1]
    LB --> B2[Backend 2]
    LB --> B3[Backend 3]

    B1 --> Redis[(Redis-Warteschlange)]
    B2 --> Redis
    B3 --> Redis

    B1 --> PG[(PostgreSQL)]
    B2 --> PG
    B3 --> PG

    B1 --> S3[(S3-Speicher)]
    B2 --> S3
    B3 --> S3

    style LB fill:#f59e0b,color:#fff
    style Redis fill:#dc2626,color:#fff
    style PG fill:#3b82f6,color:#fff
    style S3 fill:#22c55e,color:#fff
```

## Horizontale Skalierung

Für Deployments mit hohem Traffic:

1. **Lastverteiler**: nginx, HAProxy oder Cloud-LB verwenden
2. **Mehrere Backend-Instanzen**: Mehrere Gunicorn-Prozesse betreiben
3. **Gemeinsamer Speicher**: NFS oder Objektspeicher für Uploads/Ausgaben
4. **Datenbank**: PostgreSQL für den Verlauf in Betracht ziehen (statt SQLite)

---

## Ressourcenanforderungen

| Deployment | CPU | RAM | Speicher |
|------------|-----|-----|---------|
| Entwicklung | 2 Kerne | 4 GB | 10 GB |
| Klein (< 100 Dok./Tag) | 4 Kerne | 8 GB | 50 GB |
| Mittel (< 1000 Dok./Tag) | 8 Kerne | 16 GB | 200 GB |
| Groß (> 1000 Dok./Tag) | 16+ Kerne | 32 GB+ | 500 GB+ |

---

## Lastausgleich mit Nginx

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

        # Sticky Sessions für Job-Polling
        ip_hash;
    }
}
```

---

## Redis-Job-Warteschlange

In der Produktion mit mehreren Workern die threadbasierte Warteschlange durch Redis ersetzen:

### Installation

```bash
pip install celery redis
```

### Konfiguration

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
    task_time_limit=600,  # 10 Minuten
    task_soft_time_limit=540,
)
```

### Task-Definition

```python
@celery.task(bind=True)
def convert_document(self, job_id: str, file_path: str, settings: dict):
    """Dokument asynchron konvertieren."""
    try:
        result = converter_service.convert(file_path, settings)
        return {'job_id': job_id, 'status': 'completed', 'result': result}
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
```

### Worker ausführen

```bash
celery -A celery_config worker --loglevel=info --concurrency=4
```

---

## Migration zu PostgreSQL

Bei mehreren Instanzen von SQLite zu PostgreSQL migrieren:

### Konfiguration

```python
# config.py
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/docling'
)
```

### Migrationsskript

```python
# migrate_to_postgres.py
import sqlite3
import psycopg2

def migrate():
    sqlite_conn = sqlite3.connect('history.db')
    pg_conn = psycopg2.connect(DATABASE_URL)

    # Daten von SQLite nach PostgreSQL kopieren
    # ...
```

---

## Objektspeicher (S3)

S3 oder kompatiblen Speicher für Uploads und Ausgaben verwenden:

### Konfiguration

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

### Dateioperationen

```python
def upload_to_s3(file_path: str, key: str):
    s3.upload_file(file_path, BUCKET_NAME, key)

def download_from_s3(key: str, file_path: str):
    s3.download_file(BUCKET_NAME, key, file_path)
```

---

## GPU-Beschleunigung

Für hohes OCR-Volumen:

### Docker mit GPU

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

### Kubernetes mit GPU

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

### Prometheus-Metriken

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Eigene Metriken
conversion_counter = metrics.counter(
    'conversions_total',
    'Gesamtzahl Konvertierungen',
    labels={'status': lambda: 'success'}
)
```

### Grafana-Dashboard

Wichtige Metriken:

- Konversionsrate (Dokumente/Minute)
- Warteschlangentiefe
- Bearbeitungszeit (p50, p95, p99)
- Fehlerrate
- Speicherverbrauch
- CPU-Auslastung

---

## Kubernetes-Deployment

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

