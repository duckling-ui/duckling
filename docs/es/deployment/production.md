# Despliegue en producción

Guía para desplegar Duckling en entornos de producción.

## Backend con Gunicorn

### Instalación

```bash
cd backend
source venv/bin/activate
pip install gunicorn
```

### Uso básico

```bash
gunicorn -w 4 -b 0.0.0.0:5001 duckling:app
```

### Configuración recomendada

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

!!! tip "Número de workers"
    Una buena regla práctica es `(2 × núcleos de CPU) + 1` workers.

---

## Compilación del frontend

```bash
cd frontend
npm run build
```

El directorio `dist/` contiene archivos estáticos listos para desplegar.

---

## Configuración de Nginx

### Configuración básica

```nginx
# /etc/nginx/sites-available/duckling
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/duckling/dist;
    index index.html;

    # Rutas del frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy de la API
    location /api/ {
        proxy_pass http://localhost:5001/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Para subida de archivos
        client_max_body_size 100M;
        proxy_read_timeout 300s;
    }
}
```

### Configuración completa para producción

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

    # Cabeceras de seguridad
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    root /var/www/duckling/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;

        # Caché de recursos estáticos
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

        # Subida de archivos
        client_max_body_size 200M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
    }
}
```

---

## Servicio systemd

Cree `/etc/systemd/system/duckling.service`:

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

### Gestionar el servicio

```bash
# Habilitar e iniciar
sudo systemctl enable duckling
sudo systemctl start duckling

# Comprobar estado
sudo systemctl status duckling

# Ver registros
sudo journalctl -u duckling -f
```

---

## Alternativa: Caddy

Para una configuración más sencilla, use Caddy:

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

## Variables de entorno

Defínalas en producción:

```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key
DEBUG=False
FLASK_HOST=127.0.0.1
MAX_CONTENT_LENGTH=209715200  # 200 MB
```

!!! danger "Seguridad"
    No use nunca el `SECRET_KEY` por defecto en producción. Genere una clave secreta aleatoria segura:

    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

---

## Comprobaciones de estado

Supervise el estado del servicio:

```bash
# Estado del backend
curl http://localhost:5001/api/health

# Respuesta
{"status": "healthy", "service": "duckling-backend"}
```

---

## Registro

### Registros de Gunicorn

```bash
# Registro de acceso
tail -f /var/log/docling/access.log

# Registro de errores
tail -f /var/log/docling/error.log
```

### Registro estructurado

Añada en la aplicación Flask:

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

## Estrategia de copias de seguridad

### Base de datos

```bash
# Copia de seguridad de la base SQLite
cp backend/history.db backups/history_$(date +%Y%m%d).db
```

### Salidas

```bash
# Copia de seguridad de archivos convertidos
tar -czf backups/outputs_$(date +%Y%m%d).tar.gz outputs/
```

### Copias de seguridad automatizadas

Añada a la crontab:

```cron
0 2 * * * /opt/duckling/scripts/backup.sh
```

