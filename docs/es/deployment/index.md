# Despliegue

Guías para desplegar Duckling en diversos entornos.

## Resumen

Duckling can be deployed in multiple ways depending on your needs:

<div class="grid cards" markdown>

-   :material-server:{ .lg .middle } __Producción__

    ---

    Desplegar con Gunicorn, Nginx y systemd

    [:octicons-arrow-right-24: Guía de producción](production.md)

-   :material-scale-balance:{ .lg .middle } __Escalado__

    ---

    Escalar para alto tráfico con balanceo de carga

    [:octicons-arrow-right-24: Guía de escalado](scaling.md)

-   :material-shield-check:{ .lg .middle } __Seguridad__

    ---

    Mejores prácticas de seguridad y endurecimiento

    [:octicons-arrow-right-24: Guía de seguridad](security.md)

</div>

## Opciones de despliegue

| Método | Mejor para | Complejidad |
|--------|----------|------------|
| Docker Compose | Despliegue rápido, pruebas | Bajo |
| Manual + Nginx | Control total, personalización | Medio |
| Kubernetes | Gran escala, nativo de la nube | Alto |

## Referencia rápida

### Docker (más simple)

```bash
docker-compose up -d --build
```

### Despliegue manual

```bash
# Backend with Gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5001 duckling:app

# Frontend build
cd frontend
npm run build
# Serve dist/ with nginx
```

## Lista de comprobación del entorno

Antes de desplegar en producción:

- [ ] Establece una `SECRET_KEY`
- [ ] Establecer `FLASK_DEBUG=false`
- [ ] Configurar CORS para tu dominio
- [ ] Habilitar HTTPS
- [ ] Establecer límites de tamaño de archivo apropiados
- [ ] Configurar proxy inverso
- [ ] Configurar monitoreo y registro

