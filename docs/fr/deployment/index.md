# Déploiement

Guides pour déployer Duckling dans différents environnements.

## Vue d'ensemble

Duckling can be deployed in multiple ways depending on your needs:

<div class="grid cards" markdown>

-   :material-server:{ .lg .middle } __Production__

    ---

    Déployer avec Gunicorn, Nginx et systemd

    [:octicons-arrow-right-24: Guide de production](production.md)

-   :material-scale-balance:{ .lg .middle } __Mise à l'échelle__

    ---

    Mettre à l'échelle pour un trafic élevé avec équilibrage de charge

    [:octicons-arrow-right-24: Guide de mise à l'échelle](scaling.md)

-   :material-shield-check:{ .lg .middle } __Sécurité__

    ---

    Bonnes pratiques de sécurité et durcissement

    [:octicons-arrow-right-24: Guide de sécurité](security.md)

</div>

## Options de déploiement

| Méthode | Idéal pour | Complexité |
|--------|----------|------------|
| Docker Compose | Déploiement rapide, tests | Faible |
| Manual + Nginx | Contrôle total, personnalisation | Moyen |
| Kubernetes | Grete échelle, cloud-native | Élevé |

## Référence rapide

### Docker (le plus simple)

```bash
docker-compose up -d --build
```

### Déploiement manuel

```bash
# Backend with Gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5001 duckling:app

# Frontend build
cd frontend
npm run build
# Serve dist/ with nginx
```

## Liste de contrôle de l'environnement

Avant de déployer en production :

- [ ] Définissez une `SECRET_KEY`
- [ ] Définir `FLASK_DEBUG=false`
- [ ] Configurer CORS pour votre domaine
- [ ] Activer HTTPS
- [ ] Définir des limites de taille de fichier appropriées
- [ ] Configurer le proxy inverse
- [ ] Configurer la surveillance et la journalisation

