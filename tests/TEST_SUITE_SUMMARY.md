# Test Suite Summary

This repository contains multiple test suites:

- **Root (pytest)**: Lightweight repository checks and documentation structure tests in `tests/`
  - `tests/test_docs.py`: Verifies MkDocs documentation structure (including the vendored Docling docs section; can optionally run `mkdocs build`)
  - `tests/test_docs_build.py`: Static regression test ensuring backend docs rebuild prefers the repo-local `./venv` MkDocs environment (for required plugins like `mkdocs-static-i18n`)
  - `tests/test_github_templates.py`: Ensures `.github/` issue and PR templates exist and include required policy pointers
  - `tests/test_docker_hardening.py`: Guards Docker hardening regressions (frontend non-root runtime, production compose hardening flags, and publish workflow security gates for scan/SBOM/signing)
- **Backend (pytest)**: API and service tests in `backend/tests/`
  - `backend/tests/conftest.py` stubs the app singleton’s `converter_service.start_conversion` (autouse) so convert endpoints are tested without spawning Docling worker threads (prevents segfaults on some platforms)
  - Includes regression tests for history reload endpoint validation and error handling in `backend/tests/test_api.py`
  - `POST /api/convert/batch`: mixed valid/rejected files (202) and all-rejected batches (400)
  - History reconciliation tests in `backend/tests/test_history.py` (`create_entry_from_disk`, `reconcile_from_disk`) and `backend/tests/test_api.py` (`POST /api/history/reconcile`)
- **Frontend (Vitest)**: UI and hook tests in `frontend/src/tests/`
  - `frontend/src/tests/utils/fileFilter.test.ts`: Supported-extension and max-size filtering for batch/folder uploads (aligned with backend allowlists)
  - `frontend/src/tests/components/DropZone.test.tsx`: Drop zone copy, disabled states, and **Choose files…** control
  - `frontend/src/hooks/useSlideOver.tsx`: Focus trap, Escape, and focus restore for dialog-style slide-over panels (used by settings, history, stats, docs)
  - `frontend/src/components/ScrollableRegion.tsx`: Focusable (`tabIndex={0}`) scroll containers with `role="region"` + `aria-label` for keyboard scrolling in long UI areas (settings, panels, export)
  - `frontend/src/tests/components/DocsPanel.test.tsx`: Ensures the in-app docs sidebar stays in sync when navigation happens inside the embedded MkDocs iframe (after docs load, flushes a macrotask so the `window` `message` listener is registered before dispatching; `waitFor` uses an extended timeout for CI)

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


