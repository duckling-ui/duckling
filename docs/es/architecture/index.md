# Arquitectura

Documentación técnica de la arquitectura de Duckling.

## Resumen

Duckling is a full-stack web application with a clear separation between frontend y backend:

```mermaid
graph LR
    A[Browser] --> B[React Frontend]
    B --> C[Flask Backend]
    C --> D[Docling Engine]
    D --> E[(Storage)]

    style A fill:#3b82f6,color:#fff
    style B fill:#1e3a5f,color:#fff
    style C fill:#14b8a6,color:#fff
    style D fill:#8b5cf6,color:#fff
    style E fill:#f59e0b,color:#fff
```

## Secciones

<div class="grid cards" markdown>

-   :material-view-dashboard:{ .lg .middle } __Resumen del sistema__

    ---

    Arquitectura de alto nivel y flujo de datos

    [:octicons-arrow-right-24: Resumen](overview.md)

-   :material-puzzle:{ .lg .middle } __Componentes__

    ---

    Detalles de componentes frontend y backend

    [:octicons-arrow-right-24: Componentes](components.md)

-   :material-chart-box:{ .lg .middle } __Diagramas__

    ---

    Diagramas de arquitectura y flujos

    [:octicons-arrow-right-24: Diagramas](diagrams.md)

</div>

## Decisiones de diseño clave

### Separación de responsabilidades

- **Frontend**: React con TypeScript para seguridad de tipos y UI moderna
- **Backend**: Flask por simplicidad y acceso al ecosistema Python
- **Motor**: Docling para conversión de documentos (biblioteca de IBM)

### Async Procesyo

Document conversion is hyled asynchronously:

1. Client uploads file
2. Server returns job ID immediately
3. Client polls for status
4. Server processes in background thread
5. Results available when complete

### Job Queue

A thread-based job queue prevents memory exhaustion:

- Maximum 2 concurrent conversions
- Jobs queued when capacity reached
- Automatic cleanup of completed jobs

### Configuración Persistence

Configuración are stored per-user session y applied per-conversion:

- Global defaults in `config.py`
- User settings stored in database (per session ID)
- Per-request overrides via API

Configuración are isolated per user session, ensuring multi-user deployments don't interfere with each other's preferences.

## Technology Stack

### Frontend

| Technology | Propósito |
|------------|---------|
| React 18 | UI framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Framer Motion | Animations |
| Axios | HTTP client |
| Vite | Build tool |

### Backend

| Technology | Propósito |
|------------|---------|
| Flask | Web framework |
| SQLAlchemy | Database ORM |
| SQLite | History storage |
| Docling | Document conversion |
| Threading | Async processing |

