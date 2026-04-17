# Montée en charge

Guide pour faire évoluer Duckling dans des déploiements à fort trafic.

## Architecture à l’échelle

```mermaid
graph LR
    LB[Équilibreur de charge]

    LB --> B1[Backend 1]
    LB --> B2[Backend 2]
    LB --> B3[Backend 3]

    B1 --> Redis[(File d’attente Redis)]
    B2 --> Redis
    B3 --> Redis

    B1 --> PG[(PostgreSQL)]
    B2 --> PG
    B3 --> PG

    B1 --> S3[(Stockage S3)]
    B2 --> S3
    B3 --> S3

    style LB fill:#f59e0b,color:#fff
    style Redis fill:#dc2626,color:#fff
    style PG fill:#3b82f6,color:#fff
    style S3 fill:#22c55e,color:#fff
```

## Mise à l’échelle horizontale

Pour les déploiements à fort trafic :

1. **Équilibreur de charge** : utiliser nginx, HAProxy ou un LB cloud
2. **Plusieurs instances backend** : exécuter plusieurs processus Gunicorn
3. **Stockage partagé** : NFS ou stockage objet pour les envois et sorties
4. **Base de données** : envisager PostgreSQL pour l’historique (à la place de SQLite)

---

## Besoins en ressources

| Déploiement | CPU | RAM | Stockage |
|------------|-----|-----|---------|
| Développement | 2 cœurs | 4 Go | 10 Go |
| Petit (< 100 docs/jour) | 4 cœurs | 8 Go | 50 Go |
| Moyen (< 1000 docs/jour) | 8 cœurs | 16 Go | 200 Go |
| Grand (> 1000 docs/jour) | 16+ cœurs | 32 Go+ | 500 Go+ |

---

## Répartition de charge avec Nginx

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

        # Sessions persistantes pour l’interrogation des jobs
        ip_hash;
    }
}
```

---

## File d’attente de jobs Redis

En production avec plusieurs workers, remplacer la file basée sur les threads par Redis :

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

### Définition de tâche

```python
@celery.task(bind=True)
def convert_document(self, job_id: str, file_path: str, settings: dict):
    """Convertir un document de façon asynchrone."""
    try:
        result = converter_service.convert(file_path, settings)
        return {'job_id': job_id, 'status': 'completed', 'result': result}
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
```

### Exécution des workers

```bash
celery -A celery_config worker --loglevel=info --concurrency=4
```

---

## Migration PostgreSQL

Pour les déploiements multi-instances, migrer de SQLite vers PostgreSQL :

### Configuration

```python
# config.py
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/docling'
)
```

### Script de migration

```python
# migrate_to_postgres.py
import sqlite3
import psycopg2

def migrate():
    sqlite_conn = sqlite3.connect('history.db')
    pg_conn = psycopg2.connect(DATABASE_URL)

    # Copier les données de SQLite vers PostgreSQL
    # ...
```

---

## Stockage objet (S3)

Utiliser S3 ou un stockage compatible pour les envois et les sorties :

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

### Opérations sur les fichiers

```python
def upload_to_s3(file_path: str, key: str):
    s3.upload_file(file_path, BUCKET_NAME, key)

def download_from_s3(key: str, file_path: str):
    s3.download_file(BUCKET_NAME, key, file_path)
```

---

## Accélération GPU

Pour un volume OCR élevé :

### Docker avec GPU

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

### Kubernetes avec GPU

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

## Supervision

### Métriques Prometheus

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Métriques personnalisées
conversion_counter = metrics.counter(
    'conversions_total',
    'Total des conversions',
    labels={'status': lambda: 'success'}
)
```

### Tableau de bord Grafana

Indicateurs clés :

- Débit de conversion (documents/minute)
- Profondeur de file
- Temps de traitement (p50, p95, p99)
- Taux d’erreur
- Utilisation mémoire
- Utilisation CPU

---

## Déploiement Kubernetes

### Ressource Kubernetes : Deployment

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

