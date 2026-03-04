# Bereitstellung

Anleitungen zur Bereitstellung von Duckling in verschiedenen Umgebungen.

## Übersicht

Duckling can be deployed in multiple ways depending on your needs:

<div class="grid cards" markdown>

-   :material-server:{ .lg .middle } __Produktion__

    ---

    Bereitstellung mit Gunicorn, Nginx und systemd

    [:octicons-arrow-right-24: Produktionsanleitung](production.md)

-   :material-scale-balance:{ .lg .middle } __Skalierung__

    ---

    Skalierung für hohen Verkehr mit Lastausgleich

    [:octicons-arrow-right-24: Skalierungsanleitung](scaling.md)

-   :material-shield-check:{ .lg .middle } __Sicherheit__

    ---

    Sicherheitsbest Practices und Härtung

    [:octicons-arrow-right-24: Sicherheitsanleitung](security.md)

</div>

## Bereitstellungsoptionen

| Methode | Am besten für | Komplexität |
|--------|----------|------------|
| Docker Compose | Schnelle Bereitstellung, Tests | Niedrig |
| Manual + Nginx | Volle Kontrolle, Anpassung | Mittel |
| Kubernetes | Großer Maßstab, Cloud-nativ | Hoch |

## Kurzreferenz

### Docker (am einfachsten)

```bash
docker-compose up -d --build
```

### Manuelle Bereitstellung

```bash
# Backend with Gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5001 duckling:app

# Frontend build
cd frontend
npm run build
# Serve dist/ with nginx
```

## Umgebungs-Checkliste

Vor der Bereitstellung in der Produktion:

- [ ] Setzenzen Sie einen starken `SECRET_KEY`
- [ ] Setzen `FLASK_DEBUG=false`
- [ ] CORS für Ihre Domain konfigurieren
- [ ] HTTPS aktivieren
- [ ] Angemessene Dateigrößenlimits setzen
- [ ] Reverse-Proxy konfigurieren
- [ ] Überwachung und Protokollierung einrichten

