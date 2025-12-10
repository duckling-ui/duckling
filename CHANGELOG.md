# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-10

### Added

- **Batch Processing**: Upload and convert multiple files at once
  - Toggle batch mode in the header
  - Process multiple documents simultaneously

- **Image & Table Extraction**:
  - Extract embedded images from documents
  - Download individual images
  - Extract tables with full data preservation
  - Export tables to CSV format
  - View table previews in the UI

- **RAG/Chunking Support**:
  - Document chunking for RAG applications
  - Configurable max tokens per chunk (64-8192)
  - Merge peers option for undersized chunks
  - Download chunks as JSON

- **Additional Export Formats**:
  - Document Tokens (`.tokens.json`)
  - RAG Chunks (`.chunks.json`)
  - Enhanced DocTags export

- **Advanced OCR Options**:
  - Multiple OCR backends: EasyOCR, Tesseract, macOS Vision, RapidOCR
  - GPU acceleration support (EasyOCR)
  - Configurable confidence threshold (0-1)
  - Bitmap area threshold control
  - Support for 28+ languages

- **Table Structure Options**:
  - Fast vs Accurate detection modes
  - Cell matching configuration
  - Structure extraction toggle

- **Image Generation Options**:
  - Generate page images
  - Extract picture images
  - Extract table images
  - Configurable image scale (0.1x - 4.0x)

- **Performance/Accelerator Options**:
  - Device selection: Auto, CPU, CUDA, MPS (Apple Silicon)
  - Thread count configuration (1-32)
  - Document timeout setting

- **New API Endpoints**:
  - `POST /api/convert/batch` - Batch conversion
  - `GET /api/convert/<job_id>/images` - List extracted images
  - `GET /api/convert/<job_id>/images/<id>` - Download image
  - `GET /api/convert/<job_id>/tables` - List extracted tables
  - `GET /api/convert/<job_id>/tables/<id>/csv` - Download table CSV
  - `GET /api/convert/<job_id>/tables/<id>/image` - Download table image
  - `GET /api/convert/<job_id>/chunks` - Get document chunks
  - `GET/PUT /api/settings/performance` - Performance settings
  - `GET/PUT /api/settings/chunking` - Chunking settings
  - `GET /api/settings/formats` - List all supported formats

### Changed

- **Settings Panel**: Completely redesigned with all new options
  - OCR section with backend selection and advanced options
  - Table section with mode selection
  - Image section with generation options
  - Performance section with device and thread settings
  - RAG/Chunking section with token configuration
  - Slider controls for numeric settings
  - Better organization and descriptions

- **Export Options**: Enhanced with tabs for different content types
  - Formats tab for export options
  - Images tab with download buttons
  - Tables tab with CSV export and preview
  - Chunks tab with RAG chunk viewer

- **DropZone**: Updated with format categories and batch mode support

- **Converter Service**: Major refactoring
  - Dynamic pipeline options based on settings
  - Support for all OCR backends
  - Image and table extraction
  - Chunk generation
  - Better error handling

### Fixed

- Confidence score calculation now uses cluster-level predictions
- Better handling of partial conversion success

## [1.1.0] - 2024-12-10

### Added

- **OCR Support**: Full OCR integration using EasyOCR
  - Support for 14+ languages including English, German, French, Spanish, Chinese, Japanese, Korean, Arabic
  - Force Full Page OCR option for fully scanned documents
  - Configurable OCR settings in the Settings panel
- **Improved Confidence Calculation**: Now calculates average confidence from Docling's layout predictions

### Changed

- Updated converter service to use configurable pipeline options
- Enhanced settings panel with OCR options

## [1.0.0] - 2024-12-10

### Added

- Initial release of Docling UI
- **Frontend Features**:
  - Drag-and-drop file upload with validation
  - Real-time conversion progress indicator
  - Multi-format export options (Markdown, HTML, JSON, DocTags, Plain Text)
  - Settings panel for OCR, table extraction, and image handling
  - Conversion history panel with search functionality
  - Beautiful dark theme with teal accent color
  - Responsive design for desktop and tablet
  - Animated transitions using Framer Motion

- **Backend Features**:
  - Flask REST API with CORS support
  - Async document conversion using Docling
  - SQLite-based conversion history
  - File upload management with automatic cleanup
  - Configurable conversion settings
  - Health check and format listing endpoints

- **Supported Input Formats**:
  - PDF documents
  - Microsoft Word (.docx)
  - Microsoft PowerPoint (.pptx)
  - Microsoft Excel (.xlsx)
  - HTML files
  - Markdown files
  - CSV files
  - Images (PNG, JPG, JPEG, TIFF, GIF, WebP, BMP)
  - Audio files (WAV, MP3)
  - WebVTT subtitles
  - AsciiDoc files
  - XML files

- **Export Formats**:
  - Markdown
  - HTML
  - JSON (lossless)
  - DocTags
  - Plain Text

- **Configuration Options**:
  - OCR enable/disable with language selection
  - Table structure extraction
  - Image extraction and classification
  - Default output format preference

- **Developer Experience**:
  - Comprehensive test suites (pytest, vitest)
  - Docker and Docker Compose support
  - TypeScript for type safety
  - ESLint configuration
  - Clear project structure

### Security

- Input validation for file uploads
- File type restrictions
- Maximum file size limits (100MB default)
- Secure filename handling

## [Unreleased]

### Planned

- User authentication
- Cloud storage integration
- Conversion templates
- API rate limiting
- WebSocket for real-time updates
- Dark/light theme toggle
- Keyboard shortcuts
- Accessibility improvements (WCAG 2.1)

