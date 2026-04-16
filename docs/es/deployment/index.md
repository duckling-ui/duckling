# Despliegue

Guías para desplegar Duckling en distintos entornos.

## Descripción general

Duckling puede desplegarse de varias formas según sus necesidades:

<div class="grid cards" markdown>

-   :material-server:{ .lg .middle } __Producción__

    ---

    Despliegue con Gunicorn, Nginx y systemd

    [:octicons-arrow-right-24: Guía de producción](production.md)

-   :material-scale-balance:{ .lg .middle } __Escalado__

    ---

    Escalar para alto tráfico con balanceo de carga

    [:octicons-arrow-right-24: Guía de escalado](scaling.md)

-   :material-shield-check:{ .lg .middle } __Seguridad__

    ---

    Buenas prácticas de seguridad y endurecimiento

    [:octicons-arrow-right-24: Guía de seguridad](security.md)

</div>

## Opciones de despliegue

| Método | Mejor para | Complejidad |
|--------|----------|------------|
| Docker Compose | Despliegue rápido, pruebas | Baja |
| Manual + Nginx | Control total, personalización | Media |
| Kubernetes | Gran escala, nativo en la nube | Alta |

## Referencia rápida

### Docker (lo más sencillo)

```bash
docker-compose up -d --build
```

### Despliegue manual

```bash
# Backend con Gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5001 duckling:app

# Compilación del frontend
cd frontend
npm run build
# Servir dist/ con nginx
```

## Lista de comprobación del entorno

Antes de desplegar en producción:

- [ ] Establecer un `SECRET_KEY` fuerte
- [ ] Establecer `FLASK_DEBUG=false`
- [ ] Configurar CORS para su dominio
- [ ] Habilitar HTTPS
- [ ] Definir límites de tamaño de archivo adecuados
- [ ] Configurar el proxy inverso
- [ ] Configurar monitorización y registro

