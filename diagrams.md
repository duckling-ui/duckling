# Docling UI Diagrams

Mermaid diagrams for architecture documentation. Paste into [mermaid.live](https://mermaid.live/) to export as PNG/SVG.

---

## System Architecture Overview

```mermaid
flowchart LR
    subgraph FE["Frontend"]
        direction TB
        UI[React UI] --> Hooks[Hooks]
        Hooks --> Axios[API Client]
    end

    Axios <-->|REST| API

    subgraph BE["Backend"]
        direction TB
        API[Flask API] --> SVC[Services]
        SVC --> Queue[Job Queue]
        Queue --> Doc[Docling]
    end

    Doc --> DB[(SQLite)]
    Doc --> FS[(Files)]
```

---

## Simpler Architecture (Recommended)

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

---

## Detailed Layer View

```mermaid
graph TB
    subgraph Client
        Browser[Web Browser]
    end

    subgraph Frontend
        React[React App]
        Components[Components: DropZone, Progress, Export, Settings, History]
        Hooks[Hooks: useConversion, useSettings]
        APIClient[Axios Client]
    end

    subgraph Backend
        Flask[Flask Server]
        Routes[Routes: convert, settings, history, export, docs]
        Services[Services: Converter, FileManager, History]
        JobQueue[Job Queue - 2 workers max]
    end

    subgraph Engine
        Docling[Docling DocumentConverter]
        OCR[OCR: EasyOCR, Tesseract, OcrMac]
        Extract[Extraction: Tables, Images, Chunks]
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

---

## Conversion Flow

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

---

## Batch Processing

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant Q as Queue
    participant W as Workers

    U->>F: Upload 5 Files
    F->>Q: Queue 5 Jobs

    par Process 2 at a time
        Q->>W: Job 1
        Q->>W: Job 2
    end

    W-->>Q: Job 1 Done
    Q->>W: Job 3
    W-->>Q: Job 2 Done
    Q->>W: Job 4

    Note over Q,W: Max 2 concurrent

    F->>F: Show progress per file
```

---

## Scaling Architecture

```mermaid
graph LR
    LB[Load Balancer]

    LB --> B1[Backend 1]
    LB --> B2[Backend 2]
    LB --> B3[Backend 3]

    B1 --> Redis[(Redis Queue)]
    B2 --> Redis
    B3 --> Redis

    B1 --> PG[(PostgreSQL)]
    B2 --> PG
    B3 --> PG

    B1 --> S3[(S3 Storage)]
    B2 --> S3
    B3 --> S3

    style LB fill:#f59e0b,color:#fff
    style Redis fill:#dc2626,color:#fff
    style PG fill:#3b82f6,color:#fff
    style S3 fill:#22c55e,color:#fff
```

---

## Component Tree

```mermaid
graph TD
    App[App.tsx]

    App --> Header
    App --> Main
    App --> Panels

    Main --> DropZone
    Main --> Progress
    Main --> Export

    Panels --> Settings
    Panels --> History
    Panels --> Docs

    style App fill:#3b82f6,color:#fff
    style Main fill:#14b8a6,color:#fff
    style Panels fill:#8b5cf6,color:#fff
```

---

## OCR Options

```mermaid
graph LR
    Input[Document] --> OCR{OCR Backend}

    OCR --> Easy[EasyOCR]
    OCR --> Tess[Tesseract]
    OCR --> Mac[OcrMac]
    OCR --> Rapid[RapidOCR]

    Easy --> Out[Text Output]
    Tess --> Out
    Mac --> Out
    Rapid --> Out

    style Easy fill:#22c55e,color:#fff
    style Tess fill:#3b82f6,color:#fff
    style Mac fill:#8b5cf6,color:#fff
    style Rapid fill:#f59e0b,color:#fff
```
