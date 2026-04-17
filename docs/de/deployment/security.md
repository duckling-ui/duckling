# Sicherheit

Sicherheits-Best-Practices und Härtungsleitfaden für Duckling.

## Zusammenfassung des Sicherheits-Audits

Letztes Audit: Dezember 2025

### Schwachstellen-Status

| Kategorie | Status | Hinweise |
|----------|--------|-------|
| Abhängigkeits-Schwachstellen | ✅ Behoben | flask-cors, gunicorn, werkzeug aktualisiert |
| Flask-Debug-Modus | ✅ Behoben | Nutzung von Umgebungsvariablen |
| Pfad-Traversal | ✅ Behoben | Pfadvalidierung ergänzt |
| SQL-Injection | ✅ Geschützt | SQLAlchemy-ORM mit parametrierten Abfragen |
| XSS (Cross-Site Scripting) | ⚠️ Gemindert | `dangerouslySetInnerHTML` nur für vertrauenswürdige Dokumente |
| CORS | ✅ Konfiguriert | In der Entwicklung auf localhost-Ursprünge beschränkt |

---

## Checkliste Produktionsbereitstellung

Vor dem Produktions-Deployment sicherstellen:

- [ ] Umgebungsvariable `FLASK_DEBUG=false` setzen
- [ ] Starke Umgebungsvariable `SECRET_KEY` setzen
- [ ] `FLASK_HOST` passend setzen (nicht 0.0.0.0, außer hinter Reverse-Proxy)
- [ ] CORS-Ursprünge in `backend/duckling.py` an Ihre Domain anpassen
- [ ] In der Produktion HTTPS verwenden (über Reverse-Proxy konfigurieren)
- [ ] `MAX_CONTENT_LENGTH` für Ihren Anwendungsfall setzen
- [ ] Bei Bedarf hochgeladene Dateierweiterungen prüfen und einschränken
- [ ] Ratenbegrenzung aktivieren (über Reverse-Proxy oder Middleware)
- [ ] Log-Monitoring für Sicherheitsereignisse einrichten

---

## Umgebungsvariablen

| Variable | Standard | Beschreibung |
|----------|---------|-------------|
| `FLASK_DEBUG` | `false` | Debug-Modus aktivieren (niemals in Produktion) |
| `FLASK_HOST` | `127.0.0.1` | Bind-Adresse |
| `FLASK_PORT` | `5001` | Lausch-Port |
| `SECRET_KEY` | `dev-secret-key...` | Flask-Secret (in Produktion ZWINGEND ändern) |
| `MAX_CONTENT_LENGTH` | `104857600` | Maximale Upload-Größe in Bytes (100 MB) |

!!! danger "Secret Key"
    Erzeugen Sie für die Produktion einen sicheren Secret Key:

    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

---

## Sicherheitsmaßnahmen

### Backend-Sicherheit

#### 1. Konfiguration über Umgebung

- Debug-Modus standardmäßig deaktiviert
- Secret Keys aus Umgebungsvariablen
- Standard-Bindung an localhost (127.0.0.1)

#### 2. Eingabevalidierung

- Validierung von Datei-Uploads (Whitelist der Erweiterungen)
- Dateigrößenlimits (Standard 100 MB)
- Längenlimits und Bereinigung von Suchanfragen

#### 3. Schutz vor Pfad-Traversal

- Alle Dateiauslieferungs-Endpunkte validieren Pfade
- Aufgelöste Pfade gegen erlaubte Verzeichnisse prüfen
- Verzeichnis-Traversal-Sequenzen blockieren

```python
def validate_path(path: str, allowed_dir: str) -> bool:
    """Sicherstellen, dass der Pfad das erlaubte Verzeichnis nicht verlässt."""
    resolved = os.path.realpath(path)
    return resolved.startswith(os.path.realpath(allowed_dir))
```

#### 4. Datenbanksicherheit

- SQLAlchemy-ORM verhindert SQL-Injection
- Parametrierte Abfragen für alle DB-Operationen
- LIKE-Platzhalter in Suchanfragen escaped

#### 5. CORS-Konfiguration

- Ursprünge in der Entwicklung auf localhost beschränkt
- Für Produktions-Deployments konfigurierbar

### Frontend-Sicherheit

#### 1. Inhaltssicherheit

- Dokumentation wird als vertrauenswürdiges, vom Backend erzeugtes HTML gerendert
- Kein benutzergenerierter Inhalt als HTML

#### 2. API-Kommunikation

- Alle API-Aufrufe nutzen typisierte Schnittstellen
- Fehlerantworten werden kontrolliert behandelt

---

## HTTPS-Konfiguration

### Let's Encrypt mit Certbot

```bash
# certbot installieren
sudo apt install certbot python3-certbot-nginx

# Zertifikat beziehen
sudo certbot --nginx -d docling.example.com

# Automatische Erneuerung (meist bereits eingerichtet)
sudo certbot renew --dry-run
```

### Nginx SSL-Konfiguration

```nginx
server {
    listen 443 ssl http2;
    server_name docling.example.com;

    ssl_certificate /etc/letsencrypt/live/docling.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docling.example.com/privkey.pem;

    # Moderne SSL-Konfiguration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

---

## Ratenbegrenzung

### Nginx Rate Limiting

```nginx
# Ratenlimit-Zone definieren
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

## Sicherheit bei Datei-Uploads

### Erlaubte Erweiterungen

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

### Dateinamen-Bereinigung

```python
from werkzeug.utils import secure_filename

def sanitize_filename(filename: str) -> str:
    """Dateinamen für sichere Speicherung bereinigen."""
    return secure_filename(filename)
```

---

## Sicherheits-Header

### Nginx-Header

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

### Flask-Header

```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## Abhängigkeits-Sicherheit

### Python-Abhängigkeiten

```bash
# pip-audit installieren
pip install pip-audit

# Audit ausführen
cd backend
source venv/bin/activate
pip-audit
```

### Node.js-Abhängigkeiten

```bash
# npm audit ausführen
cd frontend
npm audit

# Schwachstellen beheben
npm audit fix
```

---

## Meldung von Schwachstellen

Wenn Sie eine Sicherheitslücke entdecken:

1. **Kein** öffentliches Issue eröffnen
2. Die Maintainer direkt per E-Mail informieren mit:
   - Beschreibung der Schwachstelle
   - Schritten zur Reproduktion
   - Möglicher Auswirkung
   - Vorschlag zur Behebung (optional)

Wir antworten innerhalb von 48 Stunden und arbeiten mit Ihnen an:

- Bestätigung der Schwachstelle
- Entwicklung einer Korrektur
- Abstimmung der Offenlegung

---

## Bekannte Einschränkungen

1. **XSS im Dokumentations-Viewer**: Das Dokumentationspanel nutzt `dangerouslySetInnerHTML` für aus Markdown konvertiertes HTML. Das ist akzeptabel, weil:
   - Dokumentation nur aus lokalen Dateien kommt
   - Kein benutzergenerierter Inhalt gerendert wird
   - Inhalte serverseitig mit einer vertrauenswürdigen Markdown-Bibliothek erzeugt werden

2. **Lokaler Dateizugriff**: Die Anwendung liest und schreibt in konfigurierte Verzeichnisse. Dateisystem-Berechtigungen angemessen setzen.

3. **Keine Authentifizierung**: Die Anwendung ist für lokale/persönliche Nutzung gedacht und enthält keine Benutzerauthentifizierung. Bei Multi-User-Deployments Authentifizierung über Reverse-Proxy oder Middleware ergänzen.

