# Resumen del sistema

Arquitectura de alto nivel y flujo de datos in Duckling.

## Arquitectura Diagram

![Arquitectura del sistema](../../arch.png)

## Detailed Layer View

```mermaid
graph TB
    subgraph Client
        Browser[Web Browser]
    end

    subgraph Frontend
        React[React App]
        Components[Components]
        Hooks[Custom Hooks]
        APIClient[Axios Client]
    end

    subgraph Backend
        Flask[Flask Server]
        Routes[API Routes]
        Services[Services]
        JobQueue[Job Queue]
    end

    subgraph Engine
        Docling[DocumentConverter]
        OCR[OCR Backends]
        Extract[Extraction]
    end

    subgraph Storage
        SQLite[(SQLite DB)]
        FileSystem[(File System)]
    end

    Browser --> React
    React --> Components
    Components --> Hooks
    Hooks --> APIClient
    APIClient -->|HTTP| Flask
    Flask --> Routes
    Routes --> Services
    Services --> JobQueue
    JobQueue --> Docling
    Docling --> OCR
    Docling --> Extract
    Services --> SQLite
    Docling --> FileSystem
```

## Data Flow

### Document Conversión Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant D as Docling

    U->>F: Upload File
    F->>B: POST /convert
    B->>B: Save & Queue Job
    B-->>F: 202 job_id

    loop Poll
        F->>B: GET /status
        B-->>F: progress %
    end

    B->>D: Convert
    D-->>B: Results
    B-->>F: Complete
    F->>B: GET /result
    B-->>F: Content
    U->>F: Download
```

### Conversión Pipeline

| Step | Descripción |
|------|-------------|
| 1 | **Upload Request** - Archivo received via POST |
| 2 | **Archivo Validation & Storage** - Check extension, save to uploads/ |
| 3 | **Job Creation** - UUID assigned, entry created |
| 4 | **Queue for Procesyo** - Added to job queue |
| 5 | **Worker Thread Picks Up Job** - When capacity available |
| 6 | **DocumentConverter Initialized** - With OCR, table, image settings |
| 7 | **Document Conversión** - Extraer images, tables, chunks |
| 8 | **Export to Formatos** - MD, HTML, JSON, TXT, DocTags, Tokens |
| 9 | **Update Job Status & History** - Mark complete, store metadata |
| 10 | **Results Available** - Ready for download |

## Job Queue System

To prevent memory exhaustion when processing multiple documents:

```python
class ConverterService:
    _job_queue: Queue       # Pending jobs
    _worker_thread: Thread  # Background processor
    _max_concurrent_jobs = 2  # Limit parallel processing
```

The worker thread:

1. Monitors the job queue
2. Starts conversion threads up to the concurrent limit
3. Tracks active threads y cleans up completed ones
4. Prevents resource exhaustion during batch processing

## Database Schema

### Conversión Table

| Column | Type | Descripción |
|--------|------|-------------|
| `id` | VARCHAR(36) | Primary key (UUID) |
| `filename` | VARCHAR(255) | Sanitized filename |
| `original_filename` | VARCHAR(255) | Original upload name |
| `input_format` | VARCHAR(50) | Detected format |
| `status` | VARCHAR(50) | pending/processing/completed/failed |
| `confidence` | FLOAT | OCR confidence score |
| `error_message` | TEXT | Error details if failed |
| `output_path` | VARCHAR(500) | Path to output files |
| `settings` | TEXT | JSON settings used |
| `file_size` | FLOAT | Archivo size in bytes |
| `created_at` | DATETIME | Upload timestamp |
| `completed_at` | DATETIME | Completion timestamp |

## Seguridad Considerations

| Concern | Mitigation |
|---------|------------|
| **Archivo Upload** | Only allowed extensions accepted |
| **Archivo Size** | Configurable max (default 100MB) |
| **Archivonames** | Sanitized before storage |
| **Archivo Access** | Served through API only, no direct paths |
| **CORS** | Restricted to frontend origin |

## Rendimiento Optimizations

| Optimization | Descripción |
|--------------|-------------|
| **Converter Caching** | DocumentConverter instances cached by settings hash |
| **Job Queue** | Sequential processing prevents memory exhaustion |
| **Lazy Loading** | Heavy components loaded on demy |
| **React Query Caching** | API responses cached y deduplicated |
| **Background Procesyo** | Conversións don't block the API |

