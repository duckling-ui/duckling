# Test Suite Summary

This repository contains multiple test suites:

- **Root (pytest)**: Lightweight repository checks and documentation structure tests in `tests/`
  - `tests/test_docs.py`: Verifies MkDocs documentation structure (and can optionally run `mkdocs build`)
  - `tests/test_github_templates.py`: Ensures `.github/` issue and PR templates exist and include required policy pointers
- **Backend (pytest)**: API and service tests in `backend/tests/`
- **Frontend (Vitest)**: UI and hook tests in `frontend/src/tests/`

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


