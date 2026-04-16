# Sécurité

Bonnes pratiques de sécurité et guide de durcissement pour Duckling.

## Synthèse de l’audit de sécurité

Dernier audit : décembre 2025

### État des vulnérabilités

| Catégorie | État | Notes |
|----------|--------|-------|
| Vulnérabilités des dépendances | ✅ Corrigé | Mise à jour de flask-cors, gunicorn, werkzeug |
| Mode debug Flask | ✅ Corrigé | Utilisation des variables d’environnement |
| Traversée de chemins | ✅ Corrigé | Ajout de la validation des chemins |
| Injection SQL | ✅ Protégé | ORM SQLAlchemy avec requêtes paramétrées |
| XSS (Cross-Site Scripting) | ⚠️ Atténué | Utilisation de `dangerouslySetInnerHTML` uniquement pour des documents de confiance |
| CORS | ✅ Configuré | Limité aux origines localhost en développement |

---

## Liste de contrôle pour la production

Avant un déploiement en production, vérifier :

- [ ] Définir la variable d’environnement `FLASK_DEBUG=false`
- [ ] Définir une variable d’environnement `SECRET_KEY` forte
- [ ] Configurer `FLASK_HOST` de façon appropriée (pas 0.0.0.0 sauf derrière un reverse proxy)
- [ ] Mettre à jour les origines CORS dans `backend/duckling.py` pour correspondre à votre domaine
- [ ] Utiliser HTTPS en production (configurer via le reverse proxy)
- [ ] Définir `MAX_CONTENT_LENGTH` adapté à votre cas d’usage
- [ ] Examiner et restreindre les extensions de fichiers autorisées si nécessaire
- [ ] Activer la limitation du débit (via reverse proxy ou middleware)
- [ ] Mettre en place une surveillance des journaux pour les événements de sécurité

---

## Variables d’environnement

| Variable | Défaut | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `false` | Activer le mode debug (jamais en production) |
| `FLASK_HOST` | `127.0.0.1` | Hôte d’écoute |
| `FLASK_PORT` | `5001` | Port d’écoute |
| `SECRET_KEY` | `dev-secret-key...` | Clé secrète Flask (DOIT être changée en production) |
| `MAX_CONTENT_LENGTH` | `104857600` | Taille max d’envoi en octets (100 Mo) |

!!! danger "Clé secrète"
    Générez une clé secrète sûre pour la production :

    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

---

## Mesures de sécurité

### Sécurité du backend

#### 1. Configuration basée sur l’environnement

- Mode debug désactivé par défaut
- Clés secrètes chargées depuis les variables d’environnement
- Liaison par défaut sur localhost (127.0.0.1)

#### 2. Validation des entrées

- Validation des envois de fichiers (liste blanche d’extensions)
- Limites de taille de fichier (100 Mo par défaut)
- Limites de longueur et assainissement des requêtes de recherche

#### 3. Protection contre la traversée de chemins

- Tous les points de terminaison de service de fichiers valident les chemins
- Les chemins résolus sont vérifiés par rapport aux répertoires autorisés
- Les séquences de traversée de répertoires sont bloquées

```python
def validate_path(path: str, allowed_dir: str) -> bool:
    """S’assurer que le chemin ne sort pas du répertoire autorisé."""
    resolved = os.path.realpath(path)
    return resolved.startswith(os.path.realpath(allowed_dir))
```

#### 4. Sécurité de la base de données

- L’ORM SQLAlchemy empêche l’injection SQL
- Requêtes paramétrées pour toutes les opérations sur la base
- Caractères joker LIKE échappés dans les recherches

#### 5. Configuration CORS

- Origines limitées à localhost en développement
- Configurable pour les déploiements en production

### Sécurité du frontend

#### 1. Sécurité du contenu

- Le rendu de la documentation utilise du HTML généré par le backend de confiance
- Aucun contenu généré par l’utilisateur n’est rendu en HTML

#### 2. Communication avec l’API

- Tous les appels API utilisent des interfaces typées
- Les réponses d’erreur sont gérées proprement

---

## Configuration HTTPS

### Let’s Encrypt avec Certbot

```bash
# Installer certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir un certificat
sudo certbot --nginx -d docling.example.com

# Renouvellement automatique (généralement configuré automatiquement)
sudo certbot renew --dry-run
```

### Configuration SSL Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name docling.example.com;

    ssl_certificate /etc/letsencrypt/live/docling.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docling.example.com/privkey.pem;

    # Configuration SSL moderne
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

---

## Limitation du débit

### Limitation du débit Nginx

```nginx
# Définir une zone de limitation
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

## Sécurité des envois de fichiers

### Extensions autorisées

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

### Assainissement des noms de fichier

```python
from werkzeug.utils import secure_filename

def sanitize_filename(filename: str) -> str:
    """Assainir le nom de fichier pour un stockage sûr."""
    return secure_filename(filename)
```

---

## En-têtes de sécurité

### En-têtes Nginx

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

### En-têtes Flask

```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## Sécurité des dépendances

### Dépendances Python

```bash
# Installer pip-audit
pip install pip-audit

# Lancer l’audit
cd backend
source venv/bin/activate
pip-audit
```

### Dépendances Node.js

```bash
# Exécuter npm audit
cd frontend
npm audit

# Corriger les vulnérabilités
npm audit fix
```

---

## Signalement des vulnérabilités

Si vous découvrez une vulnérabilité de sécurité :

1. **Ne pas** ouvrir de ticket public
2. Contacter directement les mainteneurs par e-mail avec :
   - Description de la vulnérabilité
   - Étapes pour reproduire
   - Impact potentiel
   - Correctif suggéré (le cas échéant)

Nous répondrons sous 48 heures et travaillerons avec vous pour :

- Confirmer la vulnérabilité
- Développer un correctif
- Coordonner la divulgation

---

## Limitations connues

1. **XSS dans le visualiseur de documentation** : le panneau docs utilise `dangerouslySetInnerHTML` pour afficher le HTML issu du markdown. C’est acceptable car :
   - La documentation provient uniquement de fichiers locaux
   - Aucun contenu généré par l’utilisateur n’est rendu
   - Le contenu est converti côté serveur avec une bibliothèque markdown de confiance

2. **Accès aux fichiers locaux** : l’application lit et écrit dans des répertoires configurés. Assurez-vous des permissions du système de fichiers.

3. **Pas d’authentification** : l’application est conçue pour un usage local/personnel et n’inclut pas d’authentification utilisateur. Pour des déploiements multi-utilisateurs, ajoutez l’authentification via un reverse proxy ou un middleware.

