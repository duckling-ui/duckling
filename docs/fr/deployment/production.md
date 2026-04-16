# Déploiement en production

Guide pour déployer Duckling en environnements de production.

## Backend avec Gunicorn

### Installation

```bash
cd backend
source venv/bin/activate
pip install gunicorn
```

### Utilisation de base

```bash
gunicorn -w 4 -b 0.0.0.0:5001 duckling:app
```

### Configuration recommandée

```bash
gunicorn \
  --workers 4 \
  --threads 2 \
  --timeout 300 \
  --bind 0.0.0.0:5001 \
  --access-logfile /var/log/docling/access.log \
  --error-logfile /var/log/docling/error.log \
  app:app
```

!!! tip "Nombre de workers"
    Une bonne règle empirique est `(2 × cœurs CPU) + 1` workers.

---

## Build du frontend

```bash
cd frontend
npm run build
```

Le répertoire `dist/` contient les fichiers statiques prêts à être déployés.

---

## Configuration Nginx

### Configuration de base

```nginx
# /etc/nginx/sites-available/duckling
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/duckling/dist;
    index index.html;

    # Routes du frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API
    location /api/ {
        proxy_pass http://localhost:5001/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Pour les envois de fichiers
        client_max_body_size 100M;
        proxy_read_timeout 300s;
    }
}
```

### Configuration production complète

```nginx
upstream docling_backend {
    server unix:/run/duckling.sock fail_timeout=0;
}

server {
    listen 80;
    server_name docling.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name docling.example.com;

    ssl_certificate /etc/letsencrypt/live/docling.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docling.example.com/privkey.pem;

    # En-têtes de sécurité
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    root /var/www/duckling/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;

        # Mise en cache des ressources statiques
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API
    location /api/ {
        proxy_pass http://docling_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Envois de fichiers
        client_max_body_size 200M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
    }
}
```

---

## Service systemd

Créez `/etc/systemd/system/duckling.service` :

```ini
[Unit]
Description=Duckling Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/duckling/backend
Environment="PATH=/opt/duckling/backend/venv/bin"
ExecStart=/opt/duckling/backend/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/run/duckling.sock \
    --timeout 300 \
    app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Gérer le service

```bash
# Activer et démarrer
sudo systemctl enable duckling
sudo systemctl start duckling

# Vérifier le statut
sudo systemctl status duckling

# Consulter les journaux
sudo journalctl -u duckling -f
```

---

## Alternative Caddy

Pour une configuration plus simple, utilisez Caddy :

```caddyfile
docling.example.com {
    root * /var/www/duckling/dist
    file_server

    try_files {path} /index.html

    handle /api/* {
        reverse_proxy localhost:5001
    }

    header {
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
    }
}
```

---

## Variables d’environnement

À définir en production :

```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key
DEBUG=False
FLASK_HOST=127.0.0.1
MAX_CONTENT_LENGTH=209715200  # 200 Mo
```

!!! danger "Sécurité"
    N’utilisez jamais la valeur par défaut de `SECRET_KEY` en production. Générez une clé secrète aléatoire sûre :

    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

---

## Vérifications d’intégrité

Surveillez l’état du service :

```bash
# Santé du backend
curl http://localhost:5001/api/health

# Réponse
{"status": "healthy", "service": "duckling-backend"}
```

---

## Journalisation

### Journaux Gunicorn

```bash
# Journal d’accès
tail -f /var/log/docling/access.log

# Journal d’erreurs
tail -f /var/log/docling/error.log
```

### Journalisation structurée

À ajouter dans l’application Flask :

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/docling.log',
    maxBytes=10000000,
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(handler)
```

---

## Stratégie de sauvegarde

### Base de données

```bash
# Sauvegarder la base SQLite
cp backend/history.db backups/history_$(date +%Y%m%d).db
```

### Sorties

```bash
# Sauvegarder les fichiers convertis
tar -czf backups/outputs_$(date +%Y%m%d).tar.gz outputs/
```

### Sauvegardes automatisées

À ajouter à la crontab :

```cron
0 2 * * * /opt/duckling/scripts/backup.sh
```

