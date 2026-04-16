# Architecture

Documentation technique de l'architecture de Duckling.

## Vue d'ensemble

Duckling is a full-stack web application with a clear separation between frontend et backend:

```mermaid
graph LR
    A[Navigateur] --> B[Frontend React]
    B --> C[Backend Flask]
    C --> D[Moteur Docling]
    D --> E[(Stockage)]

    style A fill:#3b82f6,color:#fff
    style B fill:#1e3a5f,color:#fff
    style C fill:#14b8a6,color:#fff
    style D fill:#8b5cf6,color:#fff
    style E fill:#f59e0b,color:#fff
```

## Sections

<div class="grid cards" markdown>

-   :material-view-dashboard:{ .lg .middle } __Vue d'ensemble du système__

    ---

    Architecture de haut niveau et flux de données

    [:octicons-arrow-right-24: Vue d'ensemble](overview.md)

-   :material-puzzle:{ .lg .middle } __Composants__

    ---

    Détails des composants frontend et backend

    [:octicons-arrow-right-24: Composants](components.md)

-   :material-chart-box:{ .lg .middle } __Diagrammes__

    ---

    Diagrammes d'architecture et organigrammes

    [:octicons-arrow-right-24: Diagrammes](diagrams.md)

</div>

## Décisions de conception clés

### Séparation des préoccupations

- **Frontend**: React avec TypeScript pour la sécurité des types et une UI moderne
- **Backend**: Flask pour la simplicité et l'accès à l'écosystème Python
- **Moteur**: Docling pour la conversion de documents (bibliothèque IBM)

### Async Traitement

Document conversion is hetled asynchronously:

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

### Paramètres Persistence

Paramètres are stored per-user session et applied per-conversion:

- Global defaults in `config.py`
- User settings stored in database (per session ID)
- Per-request overrides via API

Paramètres are isolated per user session, ensuring multi-user deployments don't interfere with each other's preferences.

## Technology Stack

### Frontend

| Technology | Objectif |
|------------|---------|
| React 18 | UI framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Framer Motion | Animations |
| Axios | HTTP client |
| Vite | Build tool |

### Backend

| Technology | Objectif |
|------------|---------|
| Flask | Web framework |
| SQLAlchemy | Database ORM |
| SQLite | History storage |
| Docling | Document conversion |
| Threading | Async processing |

