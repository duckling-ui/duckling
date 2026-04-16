# Seguridad

Buenas prácticas de seguridad y guía de endurecimiento para Duckling.

## Resumen de la auditoría de seguridad

Última auditoría: diciembre de 2025

### Estado de las vulnerabilidades

| Categoría | Estado | Notas |
|----------|--------|-------|
| Vulnerabilidades en dependencias | ✅ Corregido | Actualizados flask-cors, gunicorn, werkzeug |
| Modo depuración de Flask | ✅ Corregido | Ahora usa variables de entorno |
| Recorrido de rutas | ✅ Corregido | Añadida validación de rutas |
| Inyección SQL | ✅ Protegido | ORM SQLAlchemy con consultas parametrizadas |
| XSS (Cross-Site Scripting) | ⚠️ Mitigado | Usa `dangerouslySetInnerHTML` solo para documentos de confianza |
| CORS | ✅ Configurado | Restringido a orígenes localhost en desarrollo |

---

## Lista de comprobación para producción

Antes de desplegar en producción, asegúrese de:

- [ ] Establecer la variable de entorno `FLASK_DEBUG=false`
- [ ] Establecer una variable de entorno `SECRET_KEY` fuerte
- [ ] Configurar `FLASK_HOST` de forma adecuada (no 0.0.0.0 salvo detrás de un proxy inverso)
- [ ] Actualizar los orígenes CORS en `backend/duckling.py` para que coincidan con su dominio
- [ ] Usar HTTPS en producción (configurar mediante el proxy inverso)
- [ ] Establecer `MAX_CONTENT_LENGTH` adecuado a su caso de uso
- [ ] Revisar y restringir las extensiones de subida si es necesario
- [ ] Habilitar limitación de tasa (mediante proxy inverso o middleware)
- [ ] Configurar supervisión de registros para eventos de seguridad

---

## Variables de entorno

| Variable | Predeterminado | Descripción |
|----------|---------|-------------|
| `FLASK_DEBUG` | `false` | Activar modo depuración (nunca en producción) |
| `FLASK_HOST` | `127.0.0.1` | Host de escucha |
| `FLASK_PORT` | `5001` | Puerto de escucha |
| `SECRET_KEY` | `dev-secret-key...` | Clave secreta de Flask (DEBE cambiarse en producción) |
| `MAX_CONTENT_LENGTH` | `104857600` | Tamaño máximo de subida en bytes (100 MB) |

!!! danger "Clave secreta"
    Genere una clave secreta segura para producción:

    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

---

## Medidas de seguridad

### Seguridad del backend

#### 1. Configuración basada en el entorno

- Modo depuración desactivado por defecto
- Claves secretas cargadas desde variables de entorno
- Enlace por defecto a localhost (127.0.0.1)

#### 2. Validación de entradas

- Validación de subidas (lista blanca de extensiones)
- Límites de tamaño de archivo (100 MB por defecto)
- Límites de longitud y saneamiento de consultas de búsqueda

#### 3. Protección frente a recorrido de rutas

- Los puntos de entrega de archivos validan las rutas
- Las rutas resueltas se comprueban frente a directorios permitidos
- Se bloquean secuencias de recorrido de directorios

```python
def validate_path(path: str, allowed_dir: str) -> bool:
    """Garantizar que la ruta no sale del directorio permitido."""
    resolved = os.path.realpath(path)
    return resolved.startswith(os.path.realpath(allowed_dir))
```

#### 4. Seguridad de la base de datos

- El ORM SQLAlchemy evita la inyección SQL
- Consultas parametrizadas para todas las operaciones
- Comodines LIKE escapados en búsquedas

#### 5. Configuración CORS

- Orígenes restringidos a localhost en desarrollo
- Configurable para despliegues en producción

### Seguridad del frontend

#### 1. Seguridad del contenido

- La documentación se renderiza como HTML de confianza generado en el backend
- No se renderiza contenido generado por el usuario como HTML

#### 2. Comunicación con la API

- Todas las llamadas a la API usan interfaces tipadas
- Las respuestas de error se gestionan correctamente

---

## Configuración HTTPS

### Let's Encrypt con Certbot

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d docling.example.com

# Renovación automática (suele configurarse sola)
sudo certbot renew --dry-run
```

### Configuración SSL en Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name docling.example.com;

    ssl_certificate /etc/letsencrypt/live/docling.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docling.example.com/privkey.pem;

    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

---

## Limitación de tasa

### Limitación de tasa en Nginx

```nginx
# Definir zona de limitación
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
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/convert", methods=["POST"])
@limiter.limit("10 per minute")
def convert():
    pass
```

---

## Seguridad en subidas de archivos

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
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

### Saneamiento de nombres de archivo

```python
from werkzeug.utils import secure_filename

def sanitize_filename(filename: str) -> str:
    """Sanea el nombre de archivo para un almacenamiento seguro."""
    return secure_filename(filename)
```

---

## Cabeceras de seguridad

### Cabeceras en Nginx

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

### Cabeceras en Flask

```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## Seguridad de dependencias

### Dependencias de Python

```bash
# Instalar pip-audit
pip install pip-audit

# Ejecutar auditoría
cd backend
source venv/bin/activate
pip-audit
```

### Dependencias de Node.js

```bash
# Ejecutar npm audit
cd frontend
npm audit

# Corregir vulnerabilidades
npm audit fix
```

---

## Informar vulnerabilidades

Si descubre una vulnerabilidad de seguridad:

1. **No** abra un issue público
2. Escriba directamente a los mantenedores con:
   - Descripción de la vulnerabilidad
   - Pasos para reproducirla
   - Impacto potencial
   - Posible solución (si la tiene)

Responderemos en un plazo de 48 horas y colaboraremos con usted para:

- Confirmar la vulnerabilidad
- Desarrollar una corrección
- Coordinar la divulgación

---

## Limitaciones conocidas

1. **XSS en el visor de documentación**: el panel de documentación usa `dangerouslySetInnerHTML` para renderizar HTML convertido desde markdown. Es aceptable porque:
   - La documentación solo se sirve desde archivos locales
   - No se renderiza contenido generado por el usuario
   - El contenido se convierte en el servidor con una biblioteca markdown de confianza

2. **Acceso a archivos locales**: la aplicación lee y escribe en directorios configurados. Asegure permisos adecuados en el sistema de archivos.

3. **Sin autenticación**: la aplicación está pensada para uso local/personal y no incluye autenticación de usuario. En despliegues multiusuario, añada autenticación mediante proxy inverso o middleware.

