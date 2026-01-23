# Architecture

Technical architecture documentation for Duckling.

## Overview

Duckling is a full-stack web application with a clear separation between frontend and backend:

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

## Sections

<div class="grid cards" markdown>

-   :material-view-dashboard:{ .lg .middle } __System Overview__

    ---

    High-level architecture and data flow

    [:octicons-arrow-right-24: Overview](overview.md)

-   :material-puzzle:{ .lg .middle } __Components__

    ---

    Frontend and backend component details

    [:octicons-arrow-right-24: Components](components.md)

-   :material-chart-box:{ .lg .middle } __Diagrams__

    ---

    Architecture diagrams and flowcharts

    [:octicons-arrow-right-24: Diagrams](diagrams.md)

</div>

## Key Design Decisions

### Separation of Concerns

- **Frontend**: React with TypeScript for type safety and modern UI
- **Backend**: Flask for simplicity and Python ecosystem access
- **Engine**: Docling for document conversion (IBM's library)

### Async Processing

Document conversion is handled asynchronously:

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

### Settings Persistence

Settings are stored in JSON and applied per-conversion:

- Global defaults in `config.py`
- User settings in `user_settings.json`
- Per-request overrides via API

## Technology Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Framer Motion | Animations |
| Axios | HTTP client |
| Vite | Build tool |

### Backend

| Technology | Purpose |
|------------|---------|
| Flask | Web framework |
| SQLAlchemy | Database ORM |
| SQLite | History storage |
| Docling | Document conversion |
| Threading | Async processing |

