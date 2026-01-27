# Production Deployment

Guide for deploying Duckling in production environments.

## Backend with Gunicorn

### Installation

```bash
cd backend
source venv/bin/activate
pip install gunicorn
```

### Basic Usage

```bash
gunicorn -w 4 -b 0.0.0.0:5001 duckling:app
```

### Recommended Configuration

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

!!! tip "Worker Count"
    A good rule of thumb is `(2 × CPU cores) + 1` workers.

---

## Frontend Build

```bash
cd frontend
npm run build
```

The `dist/` directory contains static files ready for deployment.

---

## Nginx Configuration

### Basic Setup

```nginx
# /etc/nginx/sites-available/duckling
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/duckling/dist;
    index index.html;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://localhost:5001/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # For file uploads
        client_max_body_size 100M;
        proxy_read_timeout 300s;
    }
}
```

### Full Production Configuration

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

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    root /var/www/duckling/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;

        # Cache static assets
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

        # File uploads
        client_max_body_size 200M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
    }
}
```

---

## Systemd Service

Create `/etc/systemd/system/duckling.service`:

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

### Managing the Service

```bash
# Enable and start
sudo systemctl enable duckling
sudo systemctl start duckling

# Check status
sudo systemctl status duckling

# View logs
sudo journalctl -u duckling -f
```

---

## Caddy Alternative

For simpler configuration, use Caddy:

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

## Environment Variables

Set these in production:

```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key
DEBUG=False
FLASK_HOST=127.0.0.1
MAX_CONTENT_LENGTH=209715200  # 200MB
```

!!! danger "Security"
    Never use the default `SECRET_KEY` in production. Generate a secure random key:

    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

---

## Health Checks

Monitor service health:

```bash
# Backend health
curl http://localhost:5001/api/health

# Response
{"status": "healthy", "service": "duckling-backend"}
```

---

## Logging

### Gunicorn Logs

```bash
# Access log
tail -f /var/log/docling/access.log

# Error log
tail -f /var/log/docling/error.log
```

### Structured Logging

Add to the Flask app:

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

## Backup Strategy

### Database

```bash
# Backup SQLite database
cp backend/history.db backups/history_$(date +%Y%m%d).db
```

### Outputs

```bash
# Backup converted files
tar -czf backups/outputs_$(date +%Y%m%d).tar.gz outputs/
```

### Automated Backups

Add to crontab:

```cron
0 2 * * * /opt/duckling/scripts/backup.sh
```

