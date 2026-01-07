# Deployment

Guides for deploying Duckling in various environments.

## Overview

Duckling can be deployed in multiple ways depending on your needs:

<div class="grid cards" markdown>

-   :material-server:{ .lg .middle } __Production__

    ---

    Deploy with Gunicorn, Nginx, and systemd

    [:octicons-arrow-right-24: Production Guide](production.md)

-   :material-scale-balance:{ .lg .middle } __Scaling__

    ---

    Scale for high traffic with load balancing

    [:octicons-arrow-right-24: Scaling Guide](scaling.md)

-   :material-shield-check:{ .lg .middle } __Security__

    ---

    Security best practices and hardening

    [:octicons-arrow-right-24: Security Guide](security.md)

</div>

## Deployment Options

| Method | Best For | Complexity |
|--------|----------|------------|
| Docker Compose | Quick deployment, testing | Low |
| Manual + Nginx | Full control, customization | Medium |
| Kubernetes | Large scale, cloud-native | High |

## Quick Reference

### Docker (Simplest)

```bash
docker-compose up -d --build
```

### Manual Deployment

```bash
# Backend with Gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5001 app:app

# Frontend build
cd frontend
npm run build
# Serve dist/ with nginx
```

## Environment Checklist

Before deploying to production:

- [ ] Set strong `SECRET_KEY`
- [ ] Set `FLASK_DEBUG=false`
- [ ] Configure CORS for your domain
- [ ] Enable HTTPS
- [ ] Set appropriate file size limits
- [ ] Configure reverse proxy
- [ ] Set up monitoring and logging

