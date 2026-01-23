# Sicherheit

Sicherheitsbestimmungen und Härtungsleitfaden für Duckling.

## Zusammenfassung des Sicherheitsaudits

Letztes Audit: Dezember 2024

### Status der Schwachstellen

| Kategorie | Status | Hinweise |
|----------|--------|----------|
| Abhängigkeitsschwachstellen | ✅ Behoben | flask-cors, gunicorn, werkzeug aktualisiert |
| Flask-Debug-Modus | ✅ Behoben | Verwendet jetzt Umgebungsvariablen |
| Pfadmanipulation | ✅ Behoben | Pfadvalidierung hinzugefügt |
| SQL-Injection | ✅ Geschützt | Verwendung von SQLAlchemy ORM mit parametrisierten Abfragen |
| XSS (Cross-Site-Scripting) | ⚠️ Abgemildert | Verwendet dangerouslySetInnerHTML nur für vertrauenswürdige Dokumente |
| CORS | ✅ Konfiguriert | In der Entwicklung auf localhost-Ursprünge beschränkt |

---

## Checkliste für die Produktionsbereitstellung

Stellen Sie vor der Bereitstellung in der Produktion sicher:

- [ ] Umgebungsvariable `FLASK_DEBUG=false` setzen
- [ ] Eine sichere Umgebungsvariable `SECRET_KEY` festlegen
- [ ] `FLASK_HOST` entsprechend konfigurieren (nicht 0.0.0.0, es sei denn, es wird ein Reverse-Proxy verwendet)
- [ ] CORS-Ursprünge in `backend/app.py` an Ihre Domain anpassen
- [ ] HTTPS in der Produktion verwenden (Konfiguration über Reverse-Proxy)
- [ ] Geeignete `MAX_CONTENT_LENGTH` für Ihren Anwendungsfall festlegen
- [ ] Dateiupload-Erweiterungen überprüfen und ggf. einschränken
- [ ] Ratenbegrenzung aktivieren (über Reverse-Proxy oder Middleware)
- [ ] Protokollüberwachung für Sicherheitsereignisse einrichten

---

## Umgebungsvariablen

| Variable | Standardwert | Beschreibung |
|----------|--------------|--------------|
| `FLASK_DEBUG` | `false` | Debug-Modus aktivieren (niemals in der Produktion) |
| `FLASK_HOST` | `127.0.0.1` | Host, an den gebunden werden soll |
| `FLASK_PORT` | `5001` | Port, auf dem gelauscht werden soll |
| `SECRET_KEY` | `dev-secret-key...` | Flask-Geheimschlüssel (MUSS in der Produktion geändert werden) |
| `MAX_CONTENT_LENGTH` | `104857600` | Maximale Upload-Größe in Bytes (100 MB) |

!!! Gefahr „Geheimer Schlüssel“
Generieren Sie einen sicheren geheimen Schlüssel für die Produktion:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Sicherheitsmaßnahmen

### Backend-Sicherheit

#### 1. Umgebungsbasierte Konfiguration

- Debug-Modus standardmäßig deaktiviert
- Geheime Schlüssel werden aus Umgebungsvariablen geladen
- Host-Bindung standardmäßig auf localhost (127.0.0.1)

#### 2. Eingabevalidierung

- Dateiupload-Validierung (Whitelist für Dateierweiterungen)
- Dateigrößenbeschränkungen (Standard: 100 MB)
- Beschränkungen und Bereinigung der Suchabfragelänge

#### 3. Schutz vor Pfadmanipulation

- Alle Endpunkte zur Dateibereitstellung validieren Pfade
- Aufgelöste Pfade werden mit zulässigen Verzeichnissen verglichen
- Pfadmanipulationssequenzen werden blockiert

```python
def validate_path(path: str, allowed_dir: str) -> bool:
"""Stellt sicher, dass der Pfad das zulässige Verzeichnis nicht verlässt."""
resolved = os.path.realpath(path)
return resolved.startswith(os.path.realpath(allowed_dir))
```

#### 4. Datenbanksicherheit

- SQLAlchemy ORM verhindert SQL-Injection
- Parametrisierte Abfragen für alle Datenbankoperationen
- LIKE-Platzhalter werden in Suchabfragen maskiert

#### 5. CORS-Konfiguration

- Ursprünge im Entwicklungsmodus auf localhost beschränkt
- Konfigurierbar für Produktionsumgebungen

### Frontend-Sicherheit

#### 1. Inhaltssicherheit

- Die Dokumentationsanzeige verwendet vertrauenswürdiges, vom Backend generiertes HTML
- Keine benutzergenerierten Inhalte werden als HTML gerendert

#### 2. API-Kommunikation

- Alle API-Aufrufe verwenden typisierte Schnittstellen
- Fehlerantworten werden ordnungsgemäß behandelt

---

## HTTPS-Konfiguration

### Let's Encrypt mit Certbot

```bash
# Certbot installieren
sudo apt install certbot python3-certbot-nginx

# Zertifikat abrufen
sudo certbot --nginx -d docling.example.com

# Automatische Verlängerung (wird normalerweise automatisch konfiguriert)
sudo certbot renew --dry-run
```

### Nginx SSL-Konfiguration

```nginx
server {
listen 443 ssl http2;
server_name docling.example.com;

ssl_certificate /etc/letsencrypt/live/docling.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/docling.example.com/privkey.pem;

``` # Moderne SSL-Konfiguration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers off;

# HSTS
add_header Strict-Transport-Security "max-age=63072000" always;
}
```

---

## Ratenbegrenzung

### Nginx-Ratenbegrenzung

```nginx
# Ratenbegrenzungszone definieren
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
default_limits=["200 pro Tag", "50 pro Stunde"]
)

@app.route("/api/convert", methods=["POST"])
@limiter.limit("10 pro Minute")
def convert():
pass
```

---

## Sicherheit beim Dateiupload

### Zulässige Dateierweiterungen

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