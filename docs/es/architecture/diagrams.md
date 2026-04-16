# Diagramas de arquitectura

Diagramas visuales de la arquitectura de Duckling.

## Visión general de la arquitectura del sistema

```mermaid
flowchart LR
    subgraph FE["Frontend"]
        direction TB
        UI[UI React] --> Hooks[Hooks]
        Hooks --> Axios[Cliente API]
    end

    Axios <-->|REST| API

    subgraph BE["Backend"]
        direction TB
        API[API Flask] --> SVC[Servicios]
        SVC --> Queue[Cola de trabajos]
        Queue --> Doc[Docling]
    end

    Doc --> DB[(SQLite)]
    Doc --> FS[(Archivos)]
```

---

## Arquitectura simple

```mermaid
graph LR
    A[Navegador] --> B[Frontend React]
    B --> C[Backend Flask]
    C --> D[Motor Docling]
    D --> E[(Almacenamiento)]

    style A fill:#3b82f6,color:#fff
    style B fill:#1e3a5f,color:#fff
    style C fill:#14b8a6,color:#fff
    style D fill:#8b5cf6,color:#fff
    style E fill:#f59e0b,color:#fff
```

---

## Vista detallada por capas

```mermaid
graph TB
    subgraph Client
        Browser[Navegador web]
    end

    subgraph Frontend
        React[Aplicación React]
        Components[Componentes: zona de soltar, progreso, exportar, ajustes, historial]
        Hooks[Hooks: useConversion, useSettings]
        APIClient[Cliente Axios]
    end

    subgraph Backend
        Flask[Servidor Flask]
        Routes[Rutas: convert, settings, history, export, docs]
        Services[Servicios: Converter, FileManager, History]
        JobQueue[Cola de trabajos – máx. 2 workers]
    end

    subgraph Engine
        Docling[Docling DocumentConverter]
        OCR[OCR: EasyOCR, Tesseract, OcrMac]
        Extract[Extracción: tablas, imágenes, fragmentos]
    end

    subgraph Storage
        SQLite[(BD SQLite)]
        FileSystem[(Sistema de archivos)]
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

## Flujo de conversión

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend
    participant D as Docling

    U->>F: Subir archivo
    F->>B: POST /convert
    B->>B: Guardar y encolar trabajo
    B-->>F: 202 job_id

    loop Sondeo
        F->>B: GET /status
        B-->>F: progreso %
    end

    B->>D: Convertir
    D-->>B: Resultados
    B-->>F: Completado
    F->>B: GET /result
    B-->>F: Contenido
    U->>F: Descargar
```

---

## Procesamiento por lotes

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant Q as Cola
    participant W as Workers

    U->>F: Subir 5 archivos
    F->>Q: Encolar 5 trabajos

    par Procesar 2 a la vez
        Q->>W: Job 1
        Q->>W: Job 2
    end

    W-->>Q: Job 1 listo
    Q->>W: Job 3
    W-->>Q: Job 2 listo
    Q->>W: Job 4

    Note over Q,W: Máx. 2 concurrentes

    F->>F: Mostrar progreso por archivo
```

---

## Arquitectura de escalado

Para despliegues en producción con mucho tráfico:

```mermaid
graph LR
    LB[Balanceador de carga]

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

## Árbol de componentes

```mermaid
graph TD
    App[App.tsx]

    App --> Header[Cabecera]
    App --> Main[Área principal]
    App --> Panels[Paneles]

    Main --> DropZone[Zona de soltar]
    Main --> Progress[Progreso]
    Main --> Export[Exportar]

    Panels --> Settings[Ajustes]
    Panels --> History[Historial]
    Panels --> Docs[Documentación]

    style App fill:#3b82f6,color:#fff
    style Main fill:#14b8a6,color:#fff
    style Panels fill:#8b5cf6,color:#fff
```

---

## Opciones OCR

```mermaid
graph LR
    Input[Documento] --> OCR{Backend OCR}

    OCR --> Easy[EasyOCR]
    OCR --> Tess[Tesseract]
    OCR --> Mac[OcrMac]
    OCR --> Rapid[RapidOCR]

    Easy --> Out[Salida de texto]
    Tess --> Out
    Mac --> Out
    Rapid --> Out

    style Easy fill:#22c55e,color:#fff
    style Tess fill:#3b82f6,color:#fff
    style Mac fill:#8b5cf6,color:#fff
    style Rapid fill:#f59e0b,color:#fff
```

---

## Imágenes estáticas de diagramas

Si el entorno no admite el renderizado de Mermaid, hay imágenes estáticas:

- [Arquitectura del sistema](../arch.png)
- [Vista detallada por capas](../Detailed-Layer-View.png)
- [Canal de conversión](../ConversionPipeline.png)
- [Procesamiento por lotes](../BatchProcessing.png)
- [Arquitectura de escalado](../ScalingArchitecture.png)
- [Árbol de componentes](../ComponentTree.png)
- [Opciones OCR](../OCR.png)
