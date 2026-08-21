# Test Suite Summary

This repository contains multiple test suites:

- **Root (pytest)**: Lightweight repository checks and documentation structure tests in `tests/`
  - `tests/test_docs.py`: Verifies MkDocs documentation structure (including DocLang coverage in Quick Start, formats, API, and Docling hub pages; settings API examples use `.tokens.json` for Document Tokens; French quickstart DocLang section is not duplicated; `test_parity_documentation_covers_key_topics` guards pipeline/chunking/server-config doc coverage; can optionally run `mkdocs build`)
  - `tests/test_get_version.py`: Ensures `scripts/get_version.py` updates only `extra.version.default` (does not corrupt i18n `fallback_to_default`), docs workflows avoid broad `sed` on mkdocs.yml, and release version sources agree on **0.1.0** (`package.json`, `App.tsx`, `mkdocs.yml`, changelog)
  - `tests/test_docs_build.py`: Static regression test ensuring backend docs rebuild prefers the repo-local `./venv` MkDocs environment (for required plugins like `mkdocs-static-i18n`)
  - `tests/test_github_templates.py`: Ensures `.github/` issue and PR templates exist and include required policy pointers
  - `tests/test_docker_hardening.py`: Guards Docker hardening regressions (including prerelease `workflow_dispatch` / tag triggers on `publish-docker.yml`, frontend non-root runtime, production compose hardening flags, writable Docker DB path, publish workflow security gates, backend requirements pins for image-scan CVE fixes, Ray/docling-jobkit kept out of default backend requirements for Trivy publish gates, Dependabot dependency minimums for axios/vitest/python-dotenv/pytest, explicit backend Dockerfile force-reinstall enforcement for `jaraco.context`/`wheel`, and `docker-build.sh` expansions safe for macOS Bash 3.2 under `set -u`). On pull requests and `main` pushes, GitHub Actions job **Docker build script (publish parity)** (`.github/workflows/test.yml`) runs this file plus `bash -n` and Bash expansion checks aligned with `publish-docker.yml`.
- **Backend (pytest)**: API and service tests in `backend/tests/`
  - `backend/tests/conftest.py` stubs the app singleton’s `converter_service.start_conversion` (autouse) so convert endpoints are tested without spawning Docling worker threads (prevents segfaults on some platforms)
  - Includes regression tests for history reload endpoint validation and error handling in `backend/tests/test_api.py`
  - `backend/tests/test_harden_python_packages.py`: Docker image hardening script keeps pip runtime working (no `--no-deps`, no ensurepip wheel deletion)
  - `backend/tests/test_api.py`: DocLang export format listed on `/api/formats` and `/api/settings/formats` (`test_output_formats_includes_doclang`, `test_settings_formats_includes_doclang`); Document Tokens extension is `.tokens.json` (`test_settings_formats_document_tokens_extension_matches_on_disk`)
  - `backend/tests/test_converter.py`: OcrMac language normalization, `force_full_page_ocr` → `OcrMode.FULL_PAGE` shim, and `_instantiate_ocr_options` dropping fields forbidden by newer Docling OCR models (`bitmap_area_threshold`)
  - `POST /api/convert/batch`: mixed valid/rejected files (202) and all-rejected batches (400)
  - History reconciliation tests in `backend/tests/test_history.py` (`create_entry_from_disk`, `reconcile_from_disk`) and `backend/tests/test_api.py` (`POST /api/history/reconcile`)
- **Frontend (Vitest)**: UI and hook tests in `frontend/src/tests/`
  - `frontend/src/tests/utils/fileFilter.test.ts`: Supported-extension and max-size filtering for batch/folder uploads (aligned with backend allowlists)
  - `frontend/src/tests/components/DropZone.test.tsx`: Drop zone copy, disabled states, and **Choose files…** control
  - `frontend/src/hooks/useSlideOver.tsx`: Focus trap, Escape, and focus restore for dialog-style slide-over panels (used by settings, history, stats, docs)
  - `frontend/src/components/ScrollableRegion.tsx`: Focusable (`tabIndex={0}`) scroll containers with `role="region"` + `aria-label` for keyboard scrolling in long UI areas (settings, panels, export)
  - `frontend/src/tests/components/DocsPanel.test.tsx`: Ensures the in-app docs sidebar stays in sync when navigation happens inside the embedded MkDocs iframe (after docs load, flushes a macrotask so the `window` `message` listener is registered before dispatching; `waitFor` uses an extended timeout for CI)
  - `frontend/src/tests/components/ExportOptions.test.tsx`: DocLang format card when `formatsAvailable` includes `doclang`
  - `frontend/src/tests/services/api.test.ts`: expected output format list includes `doclang`

## Running tests

### Root tests

```bash
pytest tests/
```

### Backend tests

```bash
cd backend
pytest
```

### Frontend tests

```bash
cd frontend
npm test
```

The frontend suite includes a basic i18n regression test in `frontend/src/tests/i18n.test.tsx`.


