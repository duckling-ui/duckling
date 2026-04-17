# Déploiement

Guides pour déployer Duckling dans différents environnements.

## Vue d’ensemble

Duckling peut être déployé de plusieurs façons selon vos besoins :

<div class="grid cards" markdown>

-   :material-server:{ .lg .middle } __Production__

    ---

    Déploiement avec Gunicorn, Nginx et systemd

    [:octicons-arrow-right-24: Guide production](production.md)

-   :material-scale-balance:{ .lg .middle } __Montée en charge__

    ---

    Passer à l’échelle pour un trafic élevé avec répartition de charge

    [:octicons-arrow-right-24: Guide montée en charge](scaling.md)

-   :material-shield-check:{ .lg .middle } __Sécurité__

    ---

    Bonnes pratiques de sécurité et durcissement

    [:octicons-arrow-right-24: Guide sécurité](security.md)

</div>

## Options de déploiement

| Méthode | Idéal pour | Complexité |
|--------|----------|------------|
| Docker Compose | Déploiement rapide, tests | Faible |
| Manuel + Nginx | Contrôle total, personnalisation | Moyenne |
| Kubernetes | Grande échelle, cloud natif | Élevée |

## Référence rapide

### Docker (le plus simple)

```bash
docker-compose up -d --build
```

### Déploiement manuel

```bash
# Backend avec Gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5001 duckling:app

# Build du frontend
cd frontend
npm run build
# Servir dist/ avec nginx
```

## Liste de contrôle d’environnement

Avant un déploiement en production :

- [ ] Définir un `SECRET_KEY` fort
- [ ] Définir `FLASK_DEBUG=false`
- [ ] Configurer le CORS pour votre domaine
- [ ] Activer HTTPS
- [ ] Définir des limites de taille de fichier adaptées
- [ ] Configurer le reverse proxy
- [ ] Mettre en place la supervision et les journaux

