# Sécurité

Meilleures pratiques de sécurité et guide de renforcement pour Duckling.

## Résumé de l'audit de sécurité

Dernier audit : décembre 2024

### État des vulnérabilités

| Catégorie | Statut | Notes |
|----------|--------|-------|
| Vulnérabilités des dépendances | ✅ Corrigé | Mise à jour de flask-cors, gunicorn, werkzeug |
| Mode débogage Flask | ✅ Corrigé | Utilise désormais des variables d'environnement |
| Parcours de chemin | ✅ Corrigé | Ajout d'une validation de chemin |
| Injection SQL | ✅ Protégé | Utilisation de l'ORM SQLAlchemy avec des requêtes paramétrées |
| XSS (Cross-Site Scripting) | ⚠️ Atténué | Utilisation de dangerouslySetInnerHTML uniquement pour les documents de confiance |
| CORS | ✅ Configuré | Restreint aux origines localhost en développement |

---

## Liste de contrôle pour le déploiement en production

Avant de déployer en production, assurez-vous de :

- [ ] Définir la variable d'environnement `FLASK_DEBUG=false`
- [ ] Définir une variable d'environnement `SECRET_KEY` forte
- [ ] Configurer `FLASK_HOST` correctement (pas 0.0.0.0 sauf si derrière un proxy inverse)
- [ ] Mettre à jour les origines CORS dans `backend/duckling.py` pour qu'elles correspondent à votre domaine
- [ ] Utiliser HTTPS en production (à configurer via un proxy inverse)
- [ ] Définir une valeur `MAX_CONTENT_LENGTH` appropriée à votre cas d'utilisation
- [ ] Examiner et restreindre les extensions de fichiers autorisées pour le téléchargement si nécessaire
- [ ] Activer la limitation de débit (via un proxy inverse ou un middleware)
- [ ] Configurer la surveillance des journaux pour les événements de sécurité

---

## Variables d'environnement

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `FLASK_DEBUG` | `false` | Activer le mode débogage (jamais en production) |
| `FLASK_HOST` | `127.0.0.1` | Hôte sur lequel se lier |
| `FLASK_PORT` | `5001` | Port d'écoute |
| `SECRET_KEY` | `dev-secret-key...` | Clé secrète Flask (À modifier impérativement en production) |
| `MAX_CONTENT_LENGTH` | `104857600` | Taille maximale de téléchargement en octets (100 Mo) |

!!! Danger « Clé secrète »
Générez une clé secrète sécurisée pour la production :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Mesures de sécurité

### Sécurité du backend

#### 1. Configuration basée sur l'environnement

- Mode débogage désactivé par défaut
- Clés secrètes chargées à partir des variables d'environnement
- Liaison d'hôte par défaut à localhost (127.0.0.1)

#### 2. Validation des entrées

- Validation des téléchargements de fichiers (liste blanche d'extensions)
- Limites de taille des fichiers (100 Mo par défaut)
- Limites de longueur et nettoyage des requêtes de recherche

#### 3. Protection contre la traversée de répertoire

- Tous les points d'accès de fichiers valident les chemins
- Les chemins résolus sont vérifiés par rapport aux répertoires autorisés
- Les séquences de traversée de répertoire sont bloquées

```python
def validate_path(path: str, allowed_dir: str) -> bool:
"""Vérifie que le chemin ne sort pas du répertoire autorisé."""
resolved = os.path.realpath(path)
return resolved.startswith(os.path.realpath(allowed_dir))
```

#### 4. Sécurité de la base de données

- SQLAlchemy ORM empêche les injections SQL
- Requêtes paramétrées pour toutes les opérations de base de données
- Les caractères génériques LIKE sont échappés dans les requêtes de recherche

#### 5. Configuration CORS

- Origines restreintes à localhost en développement
- Configurable pour les déploiements en production

### Sécurité du frontend

#### 1. Sécurité du contenu

- Le rendu de la documentation utilise du HTML généré par le backend et considéré comme fiable
- Aucun contenu généré par l'utilisateur n'est rendu en HTML

#### 2. Communication API

- Tous les appels API utilisent des interfaces typées
- Les réponses d'erreur sont gérées correctement

---

## Configuration HTTPS

### Let's Encrypt avec Certbot

```bash
# Installer certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir le certificat
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

``` # Configuration SSL moderne
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers off;

# HSTS
add_header Strict-Transport-Security "max-age=63072000" always;
}
```

---

## Limitation du débit

### Limitation du débit avec Nginx

```nginx
# Définir la zone de limitation de débit
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
default_limits=["200 par jour", "50 par heure"]
)

@app.route("/api/convert", methods=["POST"])
@limiter.limit("10 par minute")
def convert():
pass
```

---

## Sécurité du téléchargement de fichiers

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
filename.rsplit('.', 1)[1].lower() in ALLOWED_