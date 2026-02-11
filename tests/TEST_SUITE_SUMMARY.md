# Test Suite Summary

This repository contains multiple test suites:

- **Root (pytest)**: Lightweight repository checks and documentation structure tests in `tests/`
  - `tests/test_docs.py`: Verifies MkDocs documentation structure (including the vendored Docling docs section; can optionally run `mkdocs build`)
  - `tests/test_docs_build.py`: Static regression test ensuring backend docs rebuild prefers the repo-local `./venv` MkDocs environment (for required plugins like `mkdocs-static-i18n`)
  - `tests/test_github_templates.py`: Ensures `.github/` issue and PR templates exist and include required policy pointers
- **Backend (pytest)**: API and service tests in `backend/tests/`
  - Includes regression tests for history reload endpoint validation and error handling in `backend/tests/test_api.py`
  - History reconciliation tests in `backend/tests/test_history.py` (`create_entry_from_disk`, `reconcile_from_disk`) and `backend/tests/test_api.py` (`POST /api/history/reconcile`)
- **Frontend (Vitest)**: UI and hook tests in `frontend/src/tests/`
  - `frontend/src/tests/components/DocsPanel.test.tsx`: Ensures the in-app docs sidebar stays in sync when navigation happens inside the embedded MkDocs iframe

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


