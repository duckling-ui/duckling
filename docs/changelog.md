# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Latest release:** [0.0.11](https://github.com/davidgs/duckling/releases/tag/v0.0.11) (2026-03-30)

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

## [0.0.11] - 2026-03-30

### Changed

- **Accessibility**: Contributing docs add [Accessibility](contributing/accessibility.md) and MkDocs nav entry; built docs use link underlines, higher-contrast secondary text in `stylesheets/extra.css`, and `javascripts/scrollable-focus.js` for keyboard-scrollable code/tables, search dialog naming, and unique scrollable regions. See root `CHANGELOG.md` for web UI changes.
- **Upload UX**: Toolbar batch toggle removed; one drop zone supports single file, multiple files, folders, and multi-line URLs. See root `CHANGELOG.md` for full technical notes.

### Fixed

- **Docs**: Localized home pages add `aria-label` on feature card links (`card-link`). `javascripts/scrollable-focus.js` names the Material search dialog, uniquely labels code toolbars and scrollable code/table regions, and hooks `document$` for instant navigation.
- **Frontend tests**: `DocsPanel` iframe-navigation test waits for the `message` listener to attach after mocked `fetch` completes and uses a longer `waitFor` timeout so CI stays green on slower runners.

## [0.0.10a] - 2026-03-23

### Fixed

- **Backend dependencies**: One `backend/requirements.txt` for API + in-app docs builds; removed duplicate `backend/requirements-docs.txt`.

### Changed

- **Repository button**: Documentation header/sidebar repo link now says "Star on GitHub" instead of "Go to repository" to encourage starring (links to the repo where users can star).
- **Documentation**: Switched to mike for multi-version docs; deploys to gh-pages then rsyncs to duckling-ui.org. Root and `/latest/` redirect correctly; version selector works.
- **Documentation navigation**: Switched from horizontal top tabs to a single left sidebar with collapsible tree navigation; each major category (Home, Getting Started, etc.) can be expanded or collapsed.
- **Key Features tiles**: Each feature tile on the docs homepage is now a clickable link to its detailed documentation (Features or Formats page).
- **CONTRIBUTING.md**: Added DCO (Developer Certificate of Origin) sign-off requirement for all commits.
- **Contributing documentation**: Full translations for German (de), Spanish (es), and French (fr); all locales now have consistent, complete content including DCO requirements.

### Security

- Fixed Rollup path traversal (GHSA-mw96-cpmx-2vgc) and Minimatch ReDoS (GHSA-3ppc-4f35-3m26) via npm overrides in frontend: `rollup >=4.59.0`, `minimatch 9.0.6` for `@typescript-eslint/typescript-estree`.
- Fixed Werkzeug safe_join Windows device names in multi-segment paths (CVE-2026-27199, GHSA-29vq-49wr-vm6x): upgraded werkzeug 3.1.4 → 3.1.6.
- Fixed Flask session Vary: Cookie header when using `in` operator (CVE-2026-27205): upgraded flask 3.0.0 → 3.1.3.
- **SSRF prevention**: URL validation before outbound requests in `download_from_url`, `download_from_url_with_images`, and `download_image`; blocks loopback, private IPs, link-local, metadata, and dangerous schemes.
- **CodeQL security fixes**:
  - SSRF: `validate_url_safe_for_request` now returns the validated URL; all `requests.get` calls use the returned value to satisfy data-flow analysis.
  - ReDoS: HTML image extraction limited to 5MB before regex processing to mitigate polynomial regex on user-controlled content.
  - Path traversal: `delete_output_folder` now uses `validate_job_id` and `get_validated_output_dir` from security utils instead of manual checks.
  - Information exposure: Settings API error responses sanitized via `_sanitize_error_for_client` to prevent stack trace or sensitive data leakage.

## [0.0.10a] - 2026-02-24

### Added

- **Docker image publishing workflow**: GitHub Action runs when PRs are merged to `main`, building multi-platform images and pushing to Docker Hub and GitHub Container Registry (requires `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets).
- **Generate Chunks Now**: Button in RAG Chunks tab to generate chunks on demand for completed documents (`POST /api/history/{job_id}/generate-chunks`)
- **Content-addressed deduplication**: Same file + same document-affecting settings reuse stored content instead of re-converting
  - Cache hit: create symlink, load metadata, complete immediately (no Docling run)
  - Cache miss: run conversion, move output to content store, create symlink
  - Database migration `scripts/migrate_add_content_hash.py` adds `content_hash` column
- **Conversion statistics and metrics**: Extended history stats for Docling and Duckling usage analytics
  - `GET /api/history/stats` returns `avg_processing_seconds`, `ocr_backend_breakdown`, `output_format_breakdown`, `performance_device_breakdown`, `chunking_enabled_count`, `error_category_breakdown`, `source_type_breakdown`, and `queue_depth`
  - Database migration `scripts/migrate_add_stats_columns.py` adds stats columns to conversions table
  - History panel displays average processing time and queue depth when available
- **Statistics panel**: Dedicated viewer for conversion statistics (header button, "View full statistics" from History)
- **Extended statistics**: Hardware and performance metrics in the Statistics panel
  - System section: hardware type (CPU/CUDA/MPS), CPU count, current CPU usage, GPU info
  - Average pages/sec and pages/sec per CPU
  - Conversion time distribution (median, 95th, 99th percentile)
  - Pages/sec over time chart
  - CPU usage averaged during each conversion (stored in DB)
  - Database migration `scripts/migrate_add_cpu_usage_column.py` adds `cpu_usage_avg_during_conversion` column
  - CPU usage is now process-specific (Duckling backend process, runs Docling), not system-wide
  - Per-conversion config stored: `performance_device_used` (resolved from "auto" at completion), `images_classify_enabled`
  - Database migration `scripts/migrate_add_config_columns.py` adds these columns
  - Stats breakdown by hardware, OCR backend, image classifier (pages/sec, conversion time per config)
- UI language support (English `en`, Spanish `es`, French `fr`, German `de`) with a language switcher.
- Multilingual MkDocs documentation (English, Spanish, French, German) served under `/api/docs/site/<locale>/`.
- Dropzone panel category labels (Documents, Web, Images, Data) now fully internationalized.
- Docling docs section in MkDocs (curated, vendored subset of upstream Docling documentation + sync script).
- **Session-Based User Settings**: User settings stored per-session in the database instead of a shared file.

### Security

- Fixed frontend security vulnerabilities (esbuild GHSA-67mh-4wv8-2f99): Updated Vite 5→7, Vitest 1→4, and related dependencies.

### Changed

- Backend entry point renamed from `app.py` to `duckling.py` for better clarity.
- Flask application name changed to "duckling" (displays as "Serving Flask app 'duckling'").

### Fixed

- Documentation navigation now displays fully localized page names in all supported languages.
- Dropzone file format category labels now properly translate based on selected language.
- Improved documentation page title extraction with better fallback to translated names.
- In-app docs panel footer prev/next links now stay within the current sidebar category, and navigating inside the embedded docs keeps the sidebar selection in sync.
- Fixed in-app docs rebuild failing with `cannot access local variable 'shutil'` when building the MkDocs site.
- Backend docs rebuild now prefers the repo-local `./venv` MkDocs environment to ensure required plugins (like `i18n`) are available.
- Fix clicking a history entry not loading the document; now uses the history load endpoint (disk) instead of the in-memory result endpoint.
- When `document_json_path` is missing in the DB, history load now finds and loads `*.document.json` from the output directory so all history items load, not just the first.
- Document viewing panel now refreshes when loading a different history item (uses component key to remount with fresh state).
- Updated `vitest.config.ts` for Vitest 4 compatibility.
- Updated CI/CD Node.js version requirement to 22 (required for Vite 7).

## [0.0.9] - 2026-01-08

### Added

- **Custom Branding**: Duckling logo and version display in header.
- **URL-Based Document Conversion**: Convert documents from URLs with automatic image extraction for HTML.
- **Document Enrichment Options**: Code enrichment, formula enrichment, picture classification, picture description.
- **Enrichment Model Pre-Download**: Download AI models before processing.
- **Image Preview Gallery**: Visual thumbnails with lightbox viewer.
- **OCR Backend Auto-Installation**: One-click installation for pip-installable backends.
- **Format-Specific Preview**: Preview panel shows content in selected export format.
- **Rendered vs Raw Preview Mode**: Toggle for HTML and Markdown.
- **Enhanced Docker Support**: Multi-stage Dockerfiles, docker-compose variants, multi-platform builds.

### Fixed

- Multi-worker content retrieval (images, tables, results).
- HTML preview in UI.
- URL image extraction for unquoted `src` attributes.
- Documentation panel now serves pre-built MkDocs site.
- Environment variables and `.env` loading.
- Case-insensitive file extensions.
- Confidence score and OCR backend selection.

## [0.0.8] - 2026-01-07

### Changed

- **Renamed**: Project renamed from "Docling UI" to "Duckling"
  - Updated all documentation, code, and configuration files
  - Branding updated throughout the application

## [0.0.7] - 2026-01-07

### Added

- **MkDocs Documentation**: Migrated documentation to MkDocs with Material theme
  - Modern, searchable documentation site
  - Dark/light theme toggle
  - Mermaid diagram support
  - Improved navigation and organization

### Changed

- Documentation structure reorganized for better navigation
- All diagrams converted to Mermaid format for live rendering

## [0.0.6] - 2025-12-11

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

## [0.0.5] - 2025-12-10

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

## [0.0.4] - 2025-12-10

### Added

- **OCR Support**: Full OCR integration using EasyOCR
  - Support for 14+ languages
  - Force Full Page OCR option
  - Configurable OCR settings
- **Improved Confidence Calculation**: Average confidence from layout predictions

### Changed

- Updated converter service to use configurable pipeline options
- Enhanced settings panel with OCR options

## [0.0.3] - 2025-12-10

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

[Unreleased]: https://github.com/davidgs/duckling/compare/v0.0.11...HEAD
[0.0.11]: https://github.com/davidgs/duckling/compare/v0.0.10a...v0.0.11
[0.0.10a]: https://github.com/davidgs/duckling/compare/v0.0.10...v0.0.10a
[0.0.10]: https://github.com/davidgs/duckling/compare/v0.0.9...v0.0.10
[0.0.9]: https://github.com/davidgs/duckling/compare/v0.0.8...v0.0.9
[0.0.8]: https://github.com/davidgs/duckling/compare/v0.0.7...v0.0.8
[0.0.7]: https://github.com/davidgs/duckling/compare/v0.0.6...v0.0.7
[0.0.6]: https://github.com/davidgs/duckling/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/davidgs/duckling/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/davidgs/duckling/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/davidgs/duckling/releases/tag/v0.0.3
