# Security

Security best practices and hardening guide for Duckling.

## Security Audit Summary

Last audit: December 2024

### Vulnerability Status

| Category | Status | Notes |
|----------|--------|-------|
| Dependency vulnerabilities | ✅ Fixed | Updated flask-cors, gunicorn, werkzeug |
| Flask debug mode | ✅ Fixed | Now uses environment variables |
| Path traversal | ✅ Fixed | Added path validation |
| SQL injection | ✅ Protected | Using SQLAlchemy ORM with parameterized queries |
| XSS (Cross-Site Scripting) | ⚠️ Mitigated | Uses dangerouslySetInnerHTML for trusted docs only |
| CORS | ✅ Configured | Restricted to localhost origins in development |

---

## Production Deployment Checklist

Before deploying to production, ensure:

- [ ] Set `FLASK_DEBUG=false` environment variable
- [ ] Set a strong `SECRET_KEY` environment variable
- [ ] Configure `FLASK_HOST` appropriately (not 0.0.0.0 unless behind reverse proxy)
- [ ] Update CORS origins in `backend/app.py` to match your domain
- [ ] Use HTTPS in production (configure via reverse proxy)
- [ ] Set appropriate `MAX_CONTENT_LENGTH` for your use case
- [ ] Review and restrict file upload extensions if needed
- [ ] Enable rate limiting (via reverse proxy or middleware)
- [ ] Set up log monitoring for security events

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `false` | Enable debug mode (never in production) |
| `FLASK_HOST` | `127.0.0.1` | Host to bind to |
| `FLASK_PORT` | `5001` | Port to listen on |
| `SECRET_KEY` | `dev-secret-key...` | Flask secret key (MUST change in production) |
| `MAX_CONTENT_LENGTH` | `104857600` | Max upload size in bytes (100MB) |

!!! danger "Secret Key"
    Generate a secure secret key for production:

    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

---

## Security Measures

### Backend Security

#### 1. Environment-Based Configuration

- Debug mode disabled by default
- Secret keys loaded from environment variables
- Host binding defaults to localhost (127.0.0.1)

#### 2. Input Validation

- File upload validation (extension whitelist)
- File size limits (100MB default)
- Search query length limits and sanitization

#### 3. Path Traversal Protection

- All file serving endpoints validate paths
- Resolved paths checked against allowed directories
- Directory traversal sequences blocked

```python
def validate_path(path: str, allowed_dir: str) -> bool:
    """Ensure path doesn't escape allowed directory."""
    resolved = os.path.realpath(path)
    return resolved.startswith(os.path.realpath(allowed_dir))
```

#### 4. Database Security

- SQLAlchemy ORM prevents SQL injection
- Parameterized queries for all database operations
- LIKE wildcards escaped in search queries

#### 5. CORS Configuration

- Origins restricted to localhost in development
- Configurable for production deployments

### Frontend Security

#### 1. Content Security

- Documentation rendering uses trusted backend-generated HTML
- No user-generated content rendered as HTML

#### 2. API Communication

- All API calls use typed interfaces
- Error responses handled gracefully

---

## HTTPS Configuration

### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d docling.example.com

# Auto-renewal (usually configured automatically)
sudo certbot renew --dry-run
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name docling.example.com;

    ssl_certificate /etc/letsencrypt/live/docling.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docling.example.com/privkey.pem;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

---

## Rate Limiting

### Nginx Rate Limiting

```nginx
# Define rate limit zone
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

## File Upload Security

### Allowed Extensions

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

### Filename Sanitization

```python
from werkzeug.utils import secure_filename

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    return secure_filename(filename)
```

---

## Security Headers

### Nginx Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

### Flask Headers

```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## Dependency Security

### Python Dependencies

```bash
# Install pip-audit
pip install pip-audit

# Run audit
cd backend
source venv/bin/activate
pip-audit
```

### Node.js Dependencies

```bash
# Run npm audit
cd frontend
npm audit

# Fix vulnerabilities
npm audit fix
```

---

## Reporting Vulnerabilities

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Email the maintainers directly with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to:

- Confirm the vulnerability
- Develop a fix
- Coordinate disclosure

---

## Known Limitations

1. **XSS in Documentation Viewer**: The docs panel uses `dangerouslySetInnerHTML` to render markdown-converted HTML. This is acceptable because:
   - Documentation is served from local files only
   - No user-generated content is rendered
   - Content is converted server-side with trusted markdown library

2. **Local File Access**: The application reads and writes files to configured directories. Ensure proper filesystem permissions.

3. **No Authentication**: This application is designed for local/personal use and does not include user authentication. For multi-user deployments, add authentication via a reverse proxy or middleware.

