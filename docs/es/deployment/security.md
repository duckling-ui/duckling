# Seguridad

Mejores prácticas de seguridad y guía de endurecimiento para Duckling.

## Resumen de la auditoría de seguridad

Última auditoría: diciembre de 2024

### Estado de las vulnerabilidades

| Categoría | Estado | Notas |
|----------|--------|-------|
| Vulnerabilidades de dependencias | ✅ Corregido | Actualizados flask-cors, gunicorn, werkzeug |
| Modo de depuración de Flask | ✅ Corregido | Ahora usa variables de entorno |
| Recorrido de rutas | ✅ Corregido | Se agregó validación de rutas |
| Inyección SQL | ✅ Protegido | Uso de SQLAlchemy ORM con consultas parametrizadas |
| XSS (Cross-Site Scripting) | ⚠️ Mitigado | Usa dangerouslySetInnerHTML solo para documentos de confianza |
| CORS | ✅ Configurado | Restringido a orígenes de localhost en desarrollo |

---

## Lista de verificación para la implementación en producción

Antes de implementar en producción, asegúrese de:

- [ ] Establecer la variable de entorno `FLASK_DEBUG=false`
- [ ] Establecer una variable de entorno `SECRET_KEY` segura
- [ ] Configurar `FLASK_HOST` correctamente (no 0.0.0.0 a menos que esté detrás de un proxy inverso)
- [ ] Actualizar los orígenes de CORS en `backend/app.py` para que coincidan con su dominio
- [ ] Usar HTTPS en producción (configurar a través de un proxy inverso)
- [ ] Establecer un `MAX_CONTENT_LENGTH` apropiado para su caso de uso
- [ ] Revisar y restringir las extensiones de carga de archivos si es necesario
- [ ] Habilitar la limitación de velocidad (a través de un proxy inverso o middleware)
- [ ] Configurar la monitorización de registros para eventos de seguridad

---

## Variables de entorno

| Variable | Valor predeterminado | Descripción |
|----------|----------------------|-------------|
| `FLASK_DEBUG` | `false` | Habilitar el modo de depuración (nunca en producción) |
| `FLASK_HOST` | `127.0.0.1` | Host al que enlazar |
| `FLASK_PORT` | `5001` | Puerto de escucha |
| `SECRET_KEY` | `dev-secret-key...` | Clave secreta de Flask (DEBE cambiarse en producción) |
| `MAX_CONTENT_LENGTH` | `104857600` | Tamaño máximo de carga en bytes (100 MB) |

!!! Peligro: "Clave secreta"
Genere una clave secreta segura para producción:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Medidas de seguridad

### Seguridad del backend

#### 1. Configuración basada en el entorno

- Modo de depuración deshabilitado por defecto
- Claves secretas cargadas desde variables de entorno
- El enlace de host por defecto es localhost (127.0.0.1)

#### 2. Validación de entrada

- Validación de carga de archivos (lista blanca de extensiones)
- Límites de tamaño de archivo (100 MB por defecto)
- Límites de longitud y saneamiento de las consultas de búsqueda

#### 3. Protección contra la manipulación de rutas

- Todos los puntos finales de servicio de archivos validan las rutas
- Las rutas resueltas se comparan con los directorios permitidos
- Se bloquean las secuencias de manipulación de directorios

```python
def validate_path(path: str, allowed_dir: str) -> bool:
"""Asegura que la ruta no salga del directorio permitido."""
resolved = os.path.realpath(path)
return resolved.startswith(os.path.realpath(allowed_dir))
```

#### 4. Seguridad de la base de datos

- SQLAlchemy ORM previene la inyección SQL
- Consultas parametrizadas para todas las operaciones de base de datos
- Los comodines LIKE se escapan en las consultas de búsqueda

#### 5. Configuración de CORS

- Orígenes restringidos a localhost en desarrollo
- Configurable para implementaciones de producción

### Seguridad del frontend

#### 1. Seguridad del contenido

- La representación de la documentación utiliza HTML de confianza generado por el backend
- No se renderiza contenido generado por el usuario como HTML

#### 2. Comunicación de la API

- Todas las llamadas a la API utilizan interfaces tipadas
- Las respuestas de error se manejan correctamente

---

## Configuración HTTPS

### Let's Encrypt con Certbot

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d docling.example.com

# Renovación automática (generalmente configurada automáticamente)
sudo certbot renew --dry-run
```

### Configuración SSL de Nginx

```nginx
server {
listen 443 ssl http2;
server_name docling.example.com;

ssl_certificate /etc/letsencrypt/live/docling.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/docling.example.com/privkey.pem;

``` # Configuración SSL moderna
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers off;

# HSTS
add_header Strict-Transport-Security "max-age=63072000" always;
}
```

---

## Limitación de velocidad

### Limitación de velocidad con Nginx

```nginx
# Definir zona de limitación de velocidad
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
location /api/ {
limit_req zone=api burst=20 nodelay;
proxy_pass http://localhost:5001;
}
}
```

### Flask-Limiter

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
app,
key_func=get_remote_address,
default_limits=["200 por día", "50 por hora"]
)

@app.route("/api/convert", methods=["POST"])
@limiter.limit("10 por minuto")
def convert():
pass
```

---

## Seguridad en la carga de archivos

### Extensiones permitidas

```python
ALLOWED_EXTENSIONS = {
'pdf', 'docx', 'pptx', 'xlsx',
'html', 'htm', 'md', 'markdown',
'png', 'jpg', 'jpeg', 'tiff', 'gif', 'webp', 'bmp',
'asciidoc', 'adoc', 'xml'
}

def allowed_file(filename: str) -> bool:
return '.' in filename and \
filename.rsplit('.', 1)[1].lower() in ALLOWED_