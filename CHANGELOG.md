# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Latest release:** [0.0.12](https://github.com/duckling-ui/duckling/releases/tag/v0.0.12) (2026-04-17)

## [Unreleased]

### Security

- **Docker CI vulnerability gate fix**: Backend image builds now both pin (`backend/requirements.txt`) and enforce-upgrade (`backend/Dockerfile`) `jaraco.context>=6.1.0` and `wheel>=0.46.2` so Trivy publish scans do not fail on stale preinstalled package versions (`CVE-2026-23949`, `CVE-2026-24049`).
- **Docker image hardening**: Frontend production image now explicitly runs as non-root (`USER nginxuser`), backend healthcheck no longer depends on `curl`, and production/prebuilt compose defaults now enforce `read_only`, `cap_drop: ["ALL"]`, `security_opt: ["no-new-privileges:true"]`, and scoped `tmpfs` writable paths.
- **Read-only runtime fix**: Backend SQLite history DB path now uses writable Docker volume storage (`/app/data/history.db`) so history records and document-path metadata continue working with `read_only: true`.
- **Container supply chain hardening**: Publish workflow now enables build provenance, generates SBOM artifacts (Syft SPDX), scans release images with Trivy (fails on HIGH/CRITICAL), and signs published images with keyless Cosign.

### Changed

- **Docker build visibility**: `scripts/docker-build.sh` now forces plain BuildKit progress output (`BUILDKIT_PROGRESS=plain`), prints executed Docker commands, bootstraps buildx once before backend builds, timestamps major steps, and supports `--platform` / `DUCKLING_BUILD_PLATFORMS` for fast single-arch local builds (avoids multi-day `linux/arm64` QEMU builds on some hosts).
- **Docker build script reliability**: `scripts/docker-build.sh` now fails fast if the Docker daemon is unavailable and fixes boolean CLI flag handling so `--sbom`, `--provenance`, and `--push` are only passed when explicitly enabled.
- **Docker build script (macOS Bash 3.2)**: Optional `buildx` flag arrays (`BUILDX_FLAGS`, `BUILDX_OUTPUT_FLAGS`) now expand with `${name[@]+"${name[@]}"}` so an empty array no longer trips `set -u` under `/bin/bash` 3.2 (fixes `BUILDX_FLAGS[@]: unbound variable` when SBOM/provenance are off).

### Added

- **Container hardening tests**: Added `tests/test_docker_hardening.py` and updated `tests/TEST_SUITE_SUMMARY.md` to guard non-root runtime, compose hardening flags, and publish workflow security gates.
- **CI: Docker build script parity**: The `docker-build-script` job in `.github/workflows/test.yml` runs `tests/test_docker_hardening.py`, `bash -n scripts/docker-build.sh`, and ubuntu-latest Bash checks that mirror `publish-docker.yml` flag handling (`--sbom` / `--provenance` / `--push`) plus the empty optional-flags case.

### Documentation

- **UI localization**: Batch results header and counters in `frontend/src/App.tsx` now use i18n keys (`conversion.batchCompleteTitle`, `batchSucceeded`, `batchFailed`, `convertedFilesTitle`) so the “Batch Conversion Complete” view is translated in `en`/`de`/`fr`/`es`.
- **Language switcher (MkDocs)**: `docs/javascripts/language-selector.js` rewrites Material language dropdown `href`s to absolute paths so switching locale keeps the same page (and hash). Locale detection now works even when dropdown links are malformed (for example `..fr/`) or rendered without `hreflang`; works for standalone `mkdocs serve` and in-app docs under `/api/docs/site/<lang>/...`.
- **Deployment (de/fr/es)**: [index](docs/de/deployment/index.md), [production](docs/de/deployment/production.md), [scaling](docs/de/deployment/scaling.md), and [security](docs/de/deployment/security.md) fully translated (mirrored under `fr/deployment/` and `es/deployment/`); Mermaid labels localized; German deployment index overview and checklist corrected.
- **Getting started (de/fr/es)**: [Index](docs/de/getting-started/index.md), [Installation](docs/de/getting-started/installation.md), [Quick Start](docs/de/getting-started/quickstart.md), and [Docker](docs/de/getting-started/docker.md) fully translated (same filenames under `docs/fr/getting-started/` and `docs/es/getting-started/`); user-facing bash comments localized; commands unchanged; quickstart screenshots use `main-german.png` / `main-french.png` / `main-spanish.png`. [English Docker guide](docs/getting-started/docker.md) CI/CD sentence clarified (“workflow runs automatically. It:”).
- **User guide (de/fr/es)**: [Supported formats](docs/de/user-guide/formats.md) and [Screenshots gallery](docs/de/user-guide/screenshots.md) fully translated for German, French, and Spanish (`user-guide/formats.md`, `user-guide/screenshots.md` per locale; sample paragraphs, tab titles, captions; asset paths `../../assets/...`).
- **Quick Start**: [Batch Processing](docs/getting-started/quickstart.md#batch-processing) documents folder drag-and-drop, clicking the drop zone to select a folder, and **Choose files…** for multi-file selection without folder mode (localized `docs/{de,fr,es}/getting-started/quickstart.md`).
- **French user guide**: [Features](docs/fr/user-guide/features.md) headings and body text are fully translated so the integrated TOC/sidebar matches the French locale; removed duplicate **Statistics Panel** section from [English features](docs/user-guide/features.md).
- **Localized home pages**: [German](docs/de/index.md) lists Docling docs like English; [French](docs/fr/index.md) and [Spanish](docs/es/index.md) feature tiles link to locale-specific heading anchors on Features; French homepage adds a documentation list, quickstart links, and acknowledgments; Spanish homepage links [changelog](docs/es/changelog.md).
- **User guide (de/es/fr)**: [Features](docs/de/user-guide/features.md) and [Features](docs/es/user-guide/features.md) fully translated (aligned with UI strings); [Configuration](docs/de/user-guide/configuration.md), [Configuration](docs/fr/user-guide/configuration.md), and [Configuration](docs/es/user-guide/configuration.md) fully translated.
- **German docs**: [Architecture index](docs/de/architecture/index.md) and [User guide index](docs/de/user-guide/index.md) prose and headings translated (removed English fragments; corrected **Benutzerhandbuch** title typo).
- **API (de/fr/es)**: Full localization of [API index](docs/de/api/index.md), [conversion](docs/de/api/conversion.md), [settings](docs/de/api/settings.md), and [history](docs/de/api/history.md) (same filenames under `docs/fr/api/` and `docs/es/api/`).
- **Architecture (de/fr/es)**: Full localization of [overview](docs/de/architecture/overview.md), [components](docs/de/architecture/components.md), and [diagrams](docs/de/architecture/diagrams.md) per locale (Mermaid labels translated).
- **Contributing (de/fr/es)**: Full localization of all pages under `docs/{de,fr,es}/contributing/`; explicit `{#commit-messages}` and `{#dco-sign-off}` heading anchors on localized [code-style](docs/de/contributing/code-style.md) for stable links from contributing index pages.
- **Docling hub / images README**: Localized “update” sections on `docs/{de,fr,es}/docling/index.md` and screenshot contributor notes on `docs/{de,fr,es}/images/README.md`.

### Planned

- User authentication
- Cloud storage integration
- Conversion templates
- API rate limiting
- WebSocket for real-time updates
- Dark/light theme toggle
- Keyboard shortcuts
- Accessibility improvements (WCAG 2.1)

## [0.0.12] - 2026-04-17

### Fixed

- **Docs accessibility (MkDocs Material)**: `scrollable-focus.js` names the **search overlay** dialog (`.md-search[role="dialog"]`), labels each **code copy toolbar** `nav.md-code__nav` uniquely, and gives each scrollable **code/table** `role="region"` a **distinct** `aria-label` (plus `document$` re-run after instant navigation). Homepage feature cards (`card-link`) include translated **`aria-label`** on anchors in all locales.

### Changed

- **Accessibility**: Settings toggles expose `role="switch"` and labels; selects/sliders/number fields use `<label>` + `aria-describedby`; header and panel icon controls have `aria-label`; slide-overs (`SettingsPanel`, `HistoryPanel`, `StatsPanel`, `DocsPanel`) use `role="dialog"` with explicit `aria-label`, focus trap, Escape to close, and focus restore via [`useSlideOver`](frontend/src/hooks/useSlideOver.tsx); `ConversionProgress` and in-app `BatchProgress` use `role="progressbar"` and live status text; `DropZone` uses a tab pattern for Local files vs URLs; `document.documentElement.lang` follows the active locale; reduced-motion users get shorter/no spin animations; export preview and docs iframe have clearer accessible names; scrollable panels use [`ScrollableRegion`](frontend/src/components/ScrollableRegion.tsx) (`tabIndex={0}`) for keyboard scrolling; footer / prose links use underlines (not color alone); slightly higher-contrast `dark` text tokens in Tailwind; MkDocs [`extra.css`](docs/stylesheets/extra.css) improves secondary-text contrast, underlines content links, and [`scrollable-focus.js`](docs/javascripts/scrollable-focus.js) makes code/table scroll areas focusable (`i18n`, `index.css`, `mkdocs.yml` Contributing nav, [docs/contributing/accessibility.md](docs/contributing/accessibility.md)).
- **Upload UX**: The toolbar **Batch** toggle is removed. The drop zone always supports one file, multiple files, or a folder (same filtering and `/api/convert` vs `/api/convert/batch` behavior as before). The uploading subtitle uses hook state (`isUploadingMultipleFiles`). During processing, `ConversionProgress` is shown for a single active job (including a one-file batch) and `BatchProgress` only when more than one job is running. The URL tab is always a multi-line field; one non-empty line uses the single-URL API and multiple lines use batch URLs (`App`, `DropZone`, `useConversion`, i18n).
- **Dependencies**: Removed repo root `requirements-docs.txt`. CI, `scripts/docs-build.sh`, `scripts/docs-serve.sh`, and Docker helper paths install from **`backend/requirements.txt`** only (one file for API + MkDocs).

### Added

- **Folder upload (batch mode)**: Choose a folder or drag a directory onto the drop zone; files are filtered to supported extensions (and 100MB per-file limit) before calling `POST /api/convert/batch`. Plain text uploads align with the backend by allowing the `txt` extension in `Config.ALLOWED_EXTENSIONS`.
- **Batch API**: Returns **400** with an `error` and per-file `jobs` when every uploaded part is unsupported, so clients do not receive 202 with zero active conversions. Documented multipart body size limits for large folders.

### Fixed

- **Drop zone (batch)**: If a folder contains both allowed and disallowed types (e.g. `.docx` and legacy `.doc`), the app now uploads the allowed files and reports how many were skipped, instead of failing the whole selection with the picker’s long MIME list (`DropZone`, i18n).
- **Drop zone (batch)**: The main file input now uses `webkitdirectory` so macOS/Windows folder pickers **select the folder for upload** instead of drilling into it; **Choose files…** opens a normal multi-file picker for loose files (`DropZone`, i18n).
- **Drop zone**: If the library reports an unexpected “too many files” rejection with no accepted files, the UI shows a generic message instead of referring to a batch toggle (`DropZone`, i18n).
- **Backend tests**: Autouse pytest fixture stubs `converter_service.start_conversion` so `/api/convert` and `/api/convert/batch` tests do not queue real Docling work on background threads (avoids segmentation faults from native conversion code and threaded DB use after the HTTP assertion returns).
- **Frontend tests**: `DocsPanel` iframe-navigation test waits for the `message` listener effect to attach after mocked `fetch` completes (`act` + `setTimeout(0)`) and uses a longer `waitFor` timeout so CI does not dispatch before the handler is registered (fixes missing "Installation" button assertion on slower runners).
- **Docs CI**: Require `pymdown-extensions>=10.21.2` so Pygments HTML formatting does not receive `filename=None` (fixes `mkdocs build` / `architecture/components.md` on Python 3.13).
- **Python deps**: Use `markdown>=3.6,<4` (pymdown-extensions 10.21.2+ requires it) and `mkdocs>=1.6,<2` (Material 9.5+); fixes pip `ResolutionImpossible` when installing `backend/requirements.txt` on Python 3.13.

## [0.0.10a] - 2026-03-23

### Fixed

- **Backend dependencies**: Single `backend/requirements.txt` for the full backend (API + MkDocs in-app builds); removed `backend/requirements-docs.txt`. Docker backend image installs one requirements file.

### Changed

- **Documentation**: Repository button now says "Star on GitHub" instead of "Go to repository" to encourage starring (links to the repo where users can star).
- **Documentation**: Switched to mike for multi-version docs; deploys to gh-pages then rsyncs to duckling-ui.org. Root and `/latest/` redirect correctly; version selector works.

### Security

- **CodeQL security fixes** (PR #25):
  - SSRF: `validate_url_safe_for_request` now returns the validated URL; all `requests.get` calls use the returned value.
  - ReDoS: HTML image extraction limited to 5MB before regex processing.
  - Path traversal: `delete_output_folder` now uses `validate_job_id` and `get_validated_output_dir`.
  - Information exposure: Settings API error responses sanitized to prevent stack trace leakage.

## [0.0.10a] - 2026-02-24

### Added

- **Docker image publishing workflow**: GitHub Action that runs when PRs are merged to `main`
  - Builds multi-platform images (linux/amd64, linux/arm64)
  - Pushes to Docker Hub and GitHub Container Registry
  - Tags images with version from `package.json` and `latest`
  - Requires `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets

- **Generate Chunks Now**: On-demand RAG chunk generation for completed documents
  - "Generate Chunks Now" button in RAG Chunks tab when no chunks exist
  - Uses current chunking settings; saves chunks to disk for download
  - `POST /api/history/{job_id}/generate-chunks` endpoint
- **Content-addressed deduplication**: Same file + same document-affecting settings reuse stored content instead of re-converting
  - Content hash = SHA-256 of (file_hash + settings_hash), truncated to 32 chars
  - Settings hash includes only `ocr`, `tables`, `images` (excludes performance, chunking, output format)
  - Storage: `outputs/_content/{content_hash}/`; job outputs: `outputs/{job_id}/` symlinks to content store
  - Cache hit: create symlink, load metadata, populate job, complete immediately (no Docling run)
  - Cache miss: run conversion, move output to content store, create symlink, save metadata
  - Each conversion still gets its own history entry; `DoclingDocument` and outputs stored once and shared via symlinks
  - Database migration `scripts/migrate_add_content_hash.py` adds `content_hash` column
  - Orphan cleanup: `cleanup_orphaned_content()` removes content store dirs not referenced by any job symlink (runs on history delete)

- **Conversion statistics and metrics**: Extended history stats for Docling and Duckling usage analytics
  - `GET /api/history/stats` now returns `avg_processing_seconds`, `ocr_backend_breakdown`, `output_format_breakdown`, `performance_device_breakdown`, `chunking_enabled_count`, `error_category_breakdown`, `source_type_breakdown`, and `queue_depth`
  - Database migration `scripts/migrate_add_stats_columns.py` adds `processing_duration_seconds`, `ocr_backend_used`, `page_count`, and `source_type` columns to conversions table
  - Conversion completion now records processing duration, OCR backend used, and page count
  - Source type (upload, url, batch) tracked when creating history entries
  - History panel displays average processing time and queue depth when available
- **Statistics panel**: Dedicated viewer for conversion and usage statistics
  - New Statistics button in header opens a slide-in panel with full stats
  - Overview (total, success, failed, success rate, avg processing time, queue depth)
  - Storage usage (uploads, outputs, total)
  - Breakdowns: input formats, OCR backends, output formats, performance devices, source types, errors
  - Chunking-enabled count
  - "View full statistics" link in History panel opens Statistics panel
- **Extended statistics**: Hardware and performance metrics
  - System section: hardware type (CPU/CUDA/MPS), CPU count, current CPU usage, GPU info
  - Average pages/sec and pages/sec per CPU
  - Conversion time distribution (median, 95th, 99th percentile)
  - Pages/sec over time chart (Recharts)
  - CPU usage averaged during each conversion (stored in DB)
  - Database migration `scripts/migrate_add_cpu_usage_column.py` adds `cpu_usage_avg_during_conversion` column
  - CPU usage is now process-specific (Duckling backend process, runs Docling), not system-wide
  - Per-conversion config stored: `performance_device_used` (resolved from "auto" at completion), `images_classify_enabled`
  - Database migration `scripts/migrate_add_config_columns.py` adds these columns
  - Stats breakdown by hardware, OCR backend, image classifier (pages/sec, conversion time per config)

- **Document Persistence**: Processed documents are now stored on disk and can be reloaded from history
  - `DoclingDocument` objects are automatically saved as JSON files after conversion
  - Documents stored in conversion output directories (e.g., `outputs/{job_id}/document.json`)
  - Database migration script adds `document_json_path` column to track stored documents
  - New API endpoint `GET /api/history/{job_id}/load` to reload documents from history
  - Clicking on completed history entries in the UI automatically loads the stored document
  - Prevents database bloat by storing large document objects on disk instead of in the database
  - Fallback mechanism reconstructs conversion results from output files if document JSON is unavailable
- **History reconciliation**: Restore history entries from on-disk output when the database was lost or reset
  - `POST /api/history/reconcile` scans the output directory for conversion outputs that exist on disk but have no database entry
  - Creates missing history entries so they appear in the UI and can be reloaded
  - Runs automatically on application startup
- **Docling docs**: Added a curated Docling documentation section to the MkDocs site (vendored subset + sync script).

- **Internationalization (UI)**: Added French (`fr`) and German (`de`) UI translations (in addition to English/Spanish).
- **Internationalization (Docs)**: Added MkDocs multilingual documentation with `/en/`, `/es/`, `/fr/`, `/de/` locale paths served by the backend docs viewer.
- **Dropzone I18N**: Added internationalization strings for dropzone panel category labels (Documents, Web, Images, Data) in all supported languages.
- **Session-Based User Settings**: User settings are now stored per-session in the database instead of a shared file
  - Each user gets isolated settings based on their session ID
  - Prevents settings conflicts in multi-user deployments
  - Automatic migration from legacy `user_settings.json` file
  - Settings persist across server restarts (database-backed)

### Security

- **Fixed frontend security vulnerabilities**: Updated dependencies to fix esbuild vulnerability (GHSA-67mh-4wv8-2f99)
  - Updated `vite`: 5.4.21 → 7.3.1 (major update, fixes esbuild vulnerability)
  - Updated `vitest`: 1.6.1 → 4.0.18 (major update, fixes esbuild vulnerability)
  - Updated `@vitest/coverage-v8`: 1.6.1 → 4.0.18
  - Updated `@vitejs/plugin-react`: 4.7.0 → 5.1.2
- **Hardened history load path handling**: `GET /api/history/{job_id}/load` now strictly validates `job_id` and constructs output paths using a safe-join + resolved-path containment check to prevent path traversal.

### Changed

- **Backend Entry Point**: Renamed `app.py` to `duckling.py` throughout the codebase
  - Flask application now uses `Flask("duckling")` instead of `Flask(__name__)`
  - Updated all references in Dockerfiles, documentation, tests, and configuration files
  - Gunicorn now uses `duckling:app` instead of `app:app`
- **Updated frontend dependencies** (non-breaking updates):
  - `@tanstack/react-query`: 5.90.12 → 5.90.20 (patch)
  - `axios`: 1.13.2 → 1.13.3 (patch)
  - `autoprefixer`: 10.4.22 → 10.4.23 (patch)
  - `eslint-plugin-react-refresh`: 0.4.24 → 0.4.26 (patch)
  - `tailwindcss`: 3.4.18 → 3.4.19 (patch)
  - `@testing-library/react`: 14.3.1 → 16.3.2 (minor)

### Fixed

- **History load fallback crash**: Fixed an uninitialized `output_dir` reference when reconstructing results from disk (when stored document JSON is missing).
- **Docs panel navigation sync**: Footer prev/next links now navigate within the in-app docs sidebar category, and navigating inside the embedded docs keeps the sidebar selection in sync.
- **Docs rebuild error**: Fixed docs rebuild failing with `cannot access local variable 'shutil'` when building the MkDocs site.
- **Docs rebuild environment mismatch**: Backend docs rebuild now prefers the repo-local `./venv` MkDocs environment to ensure required plugins (like `i18n`) are available.
- **History panel load**: Fixed clicking a history entry not loading the document; now uses `/history/{id}/load` (disk) instead of `/convert/{id}/result` (in-memory).
- **History load for all entries**: When `document_json_path` is missing in the DB, history load now finds and loads `*.document.json` from the output directory so all history items load, not just the first.
- **Document panel not updating**: Fixed document viewing panel not refreshing when loading a different history item; now uses `key={result.job_id}` so the component remounts with fresh state.
- **Documentation Localization**: Fixed incomplete localization in documentation navigation
  - Added comprehensive translation mappings for all common page names (conversion, history, settings, components, diagrams, etc.)
  - Improved H1 title extraction from HTML with better regex patterns and error handling
  - Fixed fallback logic to use translated page names instead of English slug-based titles
  - Navigation now displays fully localized page names in Spanish, French, and German
- **Dropzone Category Labels**: Fixed missing I18N strings for file format category labels in the dropzone panel
  - Category labels (Documents, Web, Images, Data) now properly translate based on selected language
  - Added translations for all supported languages (en, es, fr, de)
- Updated `vitest.config.ts` for Vitest 4 compatibility (added `coverage.include` configuration)
- Updated CI/CD Node.js version requirement to 22 (required for Vite 7)

## [0.0.9] - 2026-01-08

### Added

- **Custom Branding**: Updated UI with Duckling logo and version display
  - Custom duckling.png logo in header and favicon
  - Version badge displayed next to app name (reads from package.json)
  - Logo used in MkDocs documentation site

- **URL-Based Document Conversion**: Convert documents directly from URLs
  - Single URL input with validation
  - Batch URL mode for converting multiple documents from URLs
  - Toggle between local file upload and URL input modes
  - Automatic file type detection from URL path and Content-Type headers
  - Support for Content-Disposition header filename extraction
  - Same file type restrictions as local uploads (PDF, DOCX, HTML, etc.)
  - **Automatic image extraction from HTML pages**: When converting HTML from URLs, images are automatically downloaded, embedded, and made available in the Image Preview Gallery
  - New API endpoints:
    - `POST /api/convert/url` - Convert single document from URL
    - `POST /api/convert/url/batch` - Convert multiple documents from URLs

- **Document Enrichment Options**: New settings for Docling's enrichment features
  - **Code Enrichment**: Enhance code blocks with language detection and syntax highlighting
  - **Formula Enrichment**: Extract LaTeX representations from mathematical formulas
  - **Picture Classification**: Classify images by type (figure, chart, diagram, photo, etc.)
  - **Picture Description**: Generate AI captions for images using vision-language models
  - New API endpoints: `GET/PUT /api/settings/enrichment`
  - Warning displayed when features that increase processing time are enabled

- **Enrichment Model Pre-Download**: Download AI models before processing documents
  - View download status for each enrichment model in Settings
  - One-click download for Picture Classifier, Picture Describer, Formula Recognizer, Code Detector
  - Progress indicator during model downloads
  - Model size displayed (~200MB to ~2GB depending on model)
  - **Version checking**: Shows clear error messages when Docling version is too old
  - **Upgrade hints**: Displays `pip install --upgrade docling` command when upgrade needed
  - New API endpoints:
    - `GET /api/settings/enrichment/models` - List all models with status
    - `GET /api/settings/enrichment/models/<id>/status` - Check specific model
    - `POST /api/settings/enrichment/models/<id>/download` - Trigger download
    - `GET /api/settings/enrichment/models/<id>/progress` - Get download progress

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

- **Format-Specific Preview**: Preview panel now shows content in the selected export format
  - Preview updates dynamically when switching between export formats
  - Content is fetched and cached for each format
  - Format name displayed in preview header

- **Rendered vs Raw Preview Mode**: Toggle between rendered and raw views for HTML and Markdown
  - HTML: View rendered HTML in isolated iframe or raw HTML source code
  - Markdown: View rendered markdown with proper table support (using `marked` library) or raw source
  - JSON: Automatically pretty-printed for readability
  - Other formats: Displayed as raw text

- **Enhanced Docker Support**: Comprehensive Docker deployment options
  - Multi-stage Dockerfiles for optimized production images
  - `docker-compose.yml` for development with local builds
  - `docker-compose.prod.yml` for production overrides with resource limits
  - `docker-compose.prebuilt.yml` for using pre-built images from registry
  - Build script (`scripts/docker-build.sh`) for easy image building and pushing
  - Automatic MkDocs documentation build during Docker build process
  - Support for custom registries and version tagging
  - Multi-platform builds (linux/amd64, linux/arm64)
  - Health checks for both frontend and backend containers
  - Non-root user for improved security
  - Fixed nginx proxy configuration for documentation assets
  - Fixed database initialization race condition with multiple workers

- **Collapsible Documentation Navigation**: Improved docs panel sidebar
  - Documents grouped by category (API, Architecture, Contributing, etc.)
  - Collapsible sections with smooth animations
  - Expand/collapse all buttons
  - Item count badges for each section
  - Visual hierarchy with indentation and border lines

### Changed

- **Confidence Display**: Improved confidence score handling
  - Confidence now only displays when valid (non-null, greater than 0)
  - Better handling of documents without OCR/layout analysis (e.g., markdown files)
  - Enhanced confidence extraction from Docling results

- **Settings Application**: User settings now properly apply to conversions
  - Conversion endpoints load saved user settings instead of defaults
  - OCR backend selection now correctly affects document processing

### Fixed

- **Multi-Worker Content Retrieval**: Fixed issues where content wasn't accessible when running with multiple Gunicorn workers
  - Images, tables, and results endpoints now fall back to scanning output directory on disk
  - Export content endpoint now falls back to reading files from disk
  - Works correctly in Docker with multiple workers where job data may be in different worker's memory
  - Properly returns empty arrays instead of 404 errors when no images/tables were extracted
  - Image count now correctly includes all image types (PNG, JPG, SVG, GIF, WebP, BMP)

- **HTML Preview in UI**: Fixed rendered HTML preview showing plain text
  - Export content API now correctly returns HTML content for preview
  - Fallback to disk-based file reading when job not in memory

- **URL Image Extraction**: Fixed issue where local/relative images weren't extracted from HTML pages
  - Updated regex to handle unquoted `src` attributes (e.g., `src=/path/to/image.png`)
  - Now correctly extracts both quoted and unquoted image URLs
  - Properly resolves relative URLs against the base URL

- **Documentation Panel**: Now serves pre-built MkDocs site for full feature support
  - Serves from `site/` directory with auto-build capability
  - Full MkDocs Material theme with icons, admonitions, and Mermaid diagrams
  - Embedded iframe display with navigation sidebar
  - "Open in new tab" button for full documentation experience
  - **Auto-build**: Backend automatically builds docs if MkDocs is installed and site doesn't exist
  - **Build button**: UI shows "Build Documentation" button when docs aren't built
  - **Rebuild button**: Footer includes rebuild option to refresh documentation
  - New API endpoint: `POST /api/docs/build` to trigger documentation build
  - Removed mermaid dependency from frontend (handled by MkDocs)

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

## [0.0.4] - 2025-12-10

### Added

- **OCR Support**: Full OCR integration using EasyOCR
  - Support for 14+ languages including English, German, French, Spanish, Chinese, Japanese, Korean, Arabic
  - Force Full Page OCR option for fully scanned documents
  - Configurable OCR settings in the Settings panel
- **Improved Confidence Calculation**: Now calculates average confidence from Docling's layout predictions

### Changed

- Updated converter service to use configurable pipeline options
- Enhanced settings panel with OCR options

## [0.0.3] - 2025-12-10

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

[Unreleased]: https://github.com/duckling-ui/duckling/compare/v0.0.12...HEAD
[0.0.12]: https://github.com/duckling-ui/duckling/compare/v0.0.10a...v0.0.12
[0.0.10a]: https://github.com/duckling-ui/duckling/compare/v0.0.10...v0.0.10a
[0.0.10]: https://github.com/duckling-ui/duckling/compare/v0.0.9...v0.0.10
[0.0.9]: https://github.com/duckling-ui/duckling/compare/v0.0.8...v0.0.9
[0.0.8]: https://github.com/duckling-ui/duckling/compare/v0.0.7...v0.0.8
[0.0.7]: https://github.com/duckling-ui/duckling/compare/v0.0.6...v0.0.7
[0.0.6]: https://github.com/duckling-ui/duckling/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/duckling-ui/duckling/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/duckling-ui/duckling/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/duckling-ui/duckling/releases/tag/v0.0.3
