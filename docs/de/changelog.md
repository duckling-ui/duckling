# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- UI language support (English `en`, Spanish `es`) with a language switcher.
- Multilingual MkDocs documentation (English + Spanish) served under `/api/docs/site/en/` and `/api/docs/site/es/`.

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
  - Mermaid diagram support
  - Improved navigation and organization

### Changed

- Documentation structure reorganized for better navigation
- All diagrams converted to Mermaid format for live rendering

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
- **Export Options**: Enhanced with tabs for different content types
- **DropZone**: Updated with format categories and batch mode support
- **Converter Service**: Major refactoring for dynamic pipeline options

### Fixed

- Confidence score calculation now uses cluster-level predictions
- Better handling of partial conversion success

## [1.1.0] - 2024-12-10

### Added

- **OCR Support**: Full OCR integration using EasyOCR
  - Support for 14+ languages
  - Force Full Page OCR option
  - Configurable OCR settings
- **Improved Confidence Calculation**: Average confidence from layout predictions

### Changed

- Updated converter service to use configurable pipeline options
- Enhanced settings panel with OCR options

## [1.0.0] - 2024-12-10

### Added

- Initial release of Duckling
- **Frontend Features**:
  - Drag-and-drop file upload
  - Real-time conversion progress
  - Multi-format export options
  - Settings panel
  - Conversion history panel
  - Dark theme with teal accent
  - Responsive design
  - Animated transitions

- **Backend Features**:
  - Flask REST API with CORS
  - Async document conversion
  - SQLite-based history
  - File upload management
  - Configurable settings
  - Health check endpoint

- **Supported Input Formats**:
  - PDF, Word, PowerPoint, Excel
  - HTML, Markdown, CSV
  - Images (PNG, JPG, TIFF, etc.)
  - AsciiDoc, XML

- **Export Formats**:
  - Markdown, HTML, JSON
  - DocTags, Plain Text

- **Developer Experience**:
  - Comprehensive test suites
  - Docker support
  - TypeScript
  - ESLint configuration

### Security

- Input validation for file uploads
- File type restrictions
- Maximum file size limits
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

