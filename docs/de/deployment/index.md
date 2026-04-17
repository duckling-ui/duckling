# Bereitstellung

Anleitungen zur Bereitstellung von Duckling in verschiedenen Umgebungen.

## Übersicht

Duckling kann je nach Anforderung auf unterschiedliche Weise bereitgestellt werden:

<div class="grid cards" markdown>

-   :material-server:{ .lg .middle } __Produktion__

    ---

    Bereitstellung mit Gunicorn, Nginx und systemd

    [:octicons-arrow-right-24: Produktionsanleitung](production.md)

-   :material-scale-balance:{ .lg .middle } __Skalierung__

    ---

    Skalierung für hohen Traffic mit Lastausgleich

    [:octicons-arrow-right-24: Skalierungsanleitung](scaling.md)

-   :material-shield-check:{ .lg .middle } __Sicherheit__

    ---

    Sicherheits-Best-Practices und Härtung

    [:octicons-arrow-right-24: Sicherheitsanleitung](security.md)

</div>

## Bereitstellungsoptionen

| Methode | Am besten für | Komplexität |
|--------|----------|------------|
| Docker Compose | Schnelle Bereitstellung, Tests | Niedrig |
| Manuell + Nginx | Volle Kontrolle, Anpassung | Mittel |
| Kubernetes | Großer Maßstab, Cloud-nativ | Hoch |

## Kurzreferenz

### Docker (am einfachsten)

```bash
docker-compose up -d --build
```

### Manuelle Bereitstellung

```bash
# Backend mit Gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5001 duckling:app

# Frontend-Build
cd frontend
npm run build
# dist/ mit nginx ausliefern
```

## Umgebungs-Checkliste

Vor der Bereitstellung in der Produktion:

- [ ] Einen starken `SECRET_KEY` setzen
- [ ] `FLASK_DEBUG=false` setzen
- [ ] CORS für Ihre Domain konfigurieren
- [ ] HTTPS aktivieren
- [ ] Angemessene Dateigrößenlimits setzen
- [ ] Reverse-Proxy konfigurieren
- [ ] Monitoring und Logging einrichten

