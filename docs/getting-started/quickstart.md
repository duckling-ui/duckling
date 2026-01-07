# Quick Start

Get started with Duckling in 5 minutes.

## Starting the Application

### Terminal 1: Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

The API will be available at `http://localhost:5001`

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:3000`

## Your First Conversion

### 1. Open the Application

Navigate to `http://localhost:3000` in your browser.

### 2. Upload a Document

Drag and drop a PDF, Word document, or image onto the drop zone, or click to browse.

![Drop Zone](../screenshot.png)

### 3. Watch the Progress

The conversion progress will be displayed in real-time.

### 4. Download Results

Once complete, choose your export format:

- **Markdown** - Great for documentation
- **HTML** - Web-ready output
- **JSON** - Full document structure
- **Plain Text** - Simple text extraction

## Basic Configuration

Click the :material-cog: **Settings** button to configure:

### OCR Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Enabled | `true` | Enable OCR for scanned documents |
| Backend | `easyocr` | OCR engine to use |
| Language | `en` | Primary language |

### Table Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Enabled | `true` | Extract tables from documents |
| Mode | `accurate` | Detection accuracy level |

### Image Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Extract | `true` | Extract embedded images |
| Scale | `1.0` | Image output scale |

## Batch Processing

To convert multiple files at once:

1. Toggle **Batch Mode** in the header
2. Drag multiple files onto the drop zone
3. All files will be processed simultaneously

!!! tip "Performance"
    Batch processing uses a job queue with a maximum of 2 concurrent conversions to prevent memory exhaustion.

## Using the API

For programmatic access, use the REST API:

```bash
# Upload and convert a document
curl -X POST http://localhost:5001/api/convert \
  -F "file=@document.pdf"

# Response
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

Check the [API Reference](../api/index.md) for complete documentation.

## Next Steps

- [Features](../user-guide/features.md) - Explore all capabilities
- [Configuration](../user-guide/configuration.md) - Advanced settings
- [API Reference](../api/index.md) - Integrate with your apps

