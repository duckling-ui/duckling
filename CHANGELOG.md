# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.0] - 2026-01-07

### Added

- **Image Preview Gallery**: Extracted images now display as visual thumbnails
  - Grid layout with actual image previews instead of icons
  - Hover actions for quick view and download
  - Full-size lightbox modal with navigation arrows
  - Click to view full-size image with download option
  - Keyboard-friendly navigation between images

- **OCR Backend Auto-Installation**: Automatic installation of OCR engines
  - Settings panel shows installation status for each OCR backend
  - One-click installation for pip-installable backends (EasyOCR, OcrMac, RapidOCR)
  - Clear status indicators (✓ installed, not installed, requires system install)
  - Helpful notes for backends requiring system-level installation (Tesseract)
  - New API endpoints for backend status and installation:
    - `GET /api/settings/ocr/backends` - Get status of all backends
    - `GET /api/settings/ocr/backends/<id>/check` - Check specific backend
    - `POST /api/settings/ocr/backends/<id>/install` - Install a backend

### Changed

- **Confidence Display**: Improved confidence score handling
  - Confidence now only displays when valid (non-null, greater than 0)
  - Better handling of documents without OCR/layout analysis (e.g., markdown files)
  - Enhanced confidence extraction from Docling results

- **Settings Application**: User settings now properly apply to conversions
  - Conversion endpoints load saved user settings instead of defaults
  - OCR backend selection now correctly affects document processing

### Fixed

- **Environment Variables**: Backend now correctly loads `.env` file from the backend directory
  - Explicit path specification for `load_dotenv()` ensures reliable loading
  - Debug mode properly controlled by `DEBUG` environment variable
- **Case-Insensitive File Extensions**: File uploads now accept uppercase extensions (e.g., `.MD`, `.PDF`)
  - Frontend accepts both uppercase and lowercase extensions
  - Backend normalizes extensions to lowercase for Docling compatibility
- **Confidence Score**: Fixed issue where confidence was always showing 0.0%
  - Now correctly handles `null` confidence values
  - Hidden for documents without confidence data
- **OCR Backend Selection**: Changing OCR backend in settings now works correctly
  - Settings are properly loaded and applied during conversion

## [2.3.0] - 2026-01-07

### Changed

- **Renamed**: Project renamed from "Docling UI" to "Duckling"
  - Updated all documentation, code, and configuration files
  - Branding updated throughout the application

## [2.2.0] - 2026-01-07

### Added

- **MkDocs Documentation**: Migrated documentation to MkDocs with Material theme
  - Modern, searchable documentation site
  - Dark/light theme toggle
  - Mermaid diagram support for live-rendered architecture diagrams
  - Improved navigation with tabs and sections
  - Code syntax highlighting with copy buttons
  - Responsive design for mobile viewing
  - Abbreviation tooltips for technical terms
- New documentation structure:
  - Getting Started guide with installation, quick start, and Docker sections
  - User Guide with features, formats, and configuration
  - API Reference split into conversion, settings, and history sections
  - Architecture documentation with system overview, components, and diagrams
  - Deployment guide with production, scaling, and security sections
  - Contributing guide with development setup, code style, and testing

### Changed

- Documentation reorganized for better discoverability
- All Mermaid diagrams now render live in the documentation
- Improved code examples with syntax highlighting

## [2.1.0] - 2024-12-11

### Security

- **CRITICAL**: Fixed Flask debug mode enabled by default in production
  - Debug mode now controlled by `FLASK_DEBUG` environment variable (default: false)
  - Host binding defaults to `127.0.0.1` instead of `0.0.0.0`
- **HIGH**: Updated vulnerable dependencies
  - `flask-cors`: 4.0.0 → 6.0.0 (CVE-2024-1681, CVE-2024-6844, CVE-2024-6866, CVE-2024-6839)
  - `gunicorn`: 21.2.0 → 23.0.0 (CVE-2024-1135, CVE-2024-6827)
  - `werkzeug`: 3.0.1 → 3.1.4 (CVE-2024-34069, CVE-2024-49766, CVE-2024-49767, CVE-2025-66221)
- **MEDIUM**: Added path traversal protection to file serving endpoints
  - Image serving validates paths don't escape allowed directories
  - Blocks directory traversal sequences (`..`)
- **MEDIUM**: Enhanced SQL query sanitization
  - Search queries now escape LIKE wildcards
  - Added query length limits
- Added comprehensive `SECURITY.md` with:
  - Security audit summary
  - Production deployment checklist
  - Environment variable documentation
  - Vulnerability reporting guidelines

### Changed

- Backend now uses environment variables for all security-sensitive configuration
- Default host changed from `0.0.0.0` to `127.0.0.1` for safer defaults

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

- Initial release of Duckling
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

