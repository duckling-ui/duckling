# Contributing to Duckling

Thank you for your interest in contributing to Duckling! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.MD), which is based on the Contributor Covenant 3.0. We are committed to providing a welcoming, safe, and inclusive environment for everyone.

Please read the full [Code of Conduct](CODE_OF_CONDUCT.MD) before contributing.

For UI and documentation accessibility expectations (ARIA patterns, MkDocs checks), see [docs/contributing/accessibility.md](docs/contributing/accessibility.md).

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, browser, versions)
   - Screenshots if applicable

### Suggesting Features

1. **Check existing issues** for similar suggestions
2. **Create a feature request** with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Write/update tests**
5. **Run tests**: Ensure all tests pass (including frontend upload helpers in `frontend/src/tests/utils/` and batch conversion cases in `backend/tests/test_api.py` when changing conversion or file-type rules)
6. **Commit with clear messages**: Follow conventional commits (see [Commit Messages](#commit-messages))
7. **Sign off all commits with DCO**: Every commit MUST include a `Signed-off-by:` line (see [DCO Sign-off](#dco-sign-off))
8. **Push to your fork**
9. **Create a Pull Request**

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Backend Setup

Use a single requirements file for the API and in-app MkDocs builds (`backend/requirements.txt`). Do not use a separate backend docs requirements file.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Database Migrations

When the schema changes, migration scripts in `scripts/` must be run for existing deployments:

```bash
python3 scripts/migrate_add_stats_columns.py   # Adds stats columns (processing_duration_seconds, etc.)
python3 scripts/migrate_add_document_path.py   # Adds document_json_path (if upgrading from older version)
python3 scripts/migrate_add_cpu_usage_column.py # Adds cpu_usage_avg_during_conversion (if upgrading from older version)
python3 scripts/migrate_add_config_columns.py   # Adds performance_device_used, images_classify_enabled
python3 scripts/migrate_add_content_hash.py     # Adds content_hash for content-addressed deduplication
```

New installations create tables with the current schema automatically.

### Running Tests

**Backend**:
```bash
cd backend
pytest --cov=. --cov-report=html
```

**Frontend**:
```bash
cd frontend
npm test
npm run test:coverage
```

When adding or modifying API endpoints, include regression tests for:
- parameter validation (e.g., disallowing path traversal patterns in route params)
- error-handling paths (to avoid 500s on missing files/data)

## Translations / i18n

Duckling supports UI and documentation translations.

### UI translations (React)

- Translations live in `frontend/src/locales/<lang>/common.json` (example: `frontend/src/locales/es/common.json`).
- The i18n setup is in `frontend/src/i18n.ts`.
- When adding new keys, prefer stable, descriptive keys (e.g. `docsPanel.title`) and keep English as the source-of-truth.

### Documentation translations (MkDocs)

- Spanish/French/German docs live under `docs/es/`, `docs/fr/`, `docs/de/` and mirror the English docs structure.
- The MkDocs i18n setup is in `mkdocs.yml` under the `i18n` plugin.
- Run a strict build before submitting changes (uses the repo docs venv in `./venv/` or creates it):

```bash
./scripts/docs-build.sh
```

#### Docling docs (vendored)

- The curated Docling documentation lives in `docs/docling/`.
- To refresh it from upstream (tracks `docling-project/docling` `main`), run:

```bash
python3 scripts/sync_docling_docs.py
```

## Code Style

### Python (Backend)

- Follow PEP 8 guidelines
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for functions and classes

```python
def convert_document(file_path: str, settings: dict) -> ConversionResult:
    """
    Convert a document using Docling.

    Args:
        file_path: Path to the document file
        settings: Conversion settings dictionary

    Returns:
        ConversionResult object with converted content
    """
    pass
```

### TypeScript/React (Frontend)

- Use functional components with hooks
- Use TypeScript for type safety
- Follow ESLint configuration
- Use meaningful component and variable names

```typescript
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export function Button({ label, onClick, disabled = false }: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
}
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]

Signed-off-by: Your Name <your.email@example.com>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(upload): add drag-and-drop file upload
fix(converter): handle large PDF files correctly
docs(readme): update installation instructions
```

### DCO Sign-off

All commits **MUST** be signed off with the [Developer Certificate of Origin (DCO)](https://developercertificate.org/). This certifies that you have the right to submit the contribution under the project's license.

Add the sign-off to every commit using `git commit -s`:

```bash
git commit -s -m "feat(upload): add drag-and-drop file upload"
```

This appends a `Signed-off-by:` line with your name and email from your Git config. You can also add it manually at the end of your commit message:

```
Signed-off-by: Your Name <your.email@example.com>
```

PRs with unsigned commits will not be merged.

## Project Structure

```
duckling/
├── backend/
│   ├── duckling.py         # Flask application entry
│   ├── config.py           # Configuration
│   ├── models/             # Database models
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   └── tests/              # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript types
│   └── tests/              # Frontend tests
└── docs/                   # Documentation
```

## Testing Guidelines

### Backend Tests

- Use pytest for testing
- Aim for >80% code coverage
- Test both success and error cases
- Use fixtures for common setup

```python
def test_convert_pdf_success(client, sample_pdf):
    response = client.post('/api/convert', data={'file': sample_pdf})
    assert response.status_code == 202
    assert 'job_id' in response.json
```

### Frontend Tests

- Use Vitest and React Testing Library
- Test component rendering and interactions
- When a test fires global events (for example `window` `message`) handled by a `useEffect` that depends on async-loaded data, ensure effects have run after the data appears (for example `await act(async () => { await new Promise((r) => setTimeout(r, 0)); })`) so CI does not race ahead of listener registration
- Mock API calls appropriately

```typescript
it('should upload file on drop', async () => {
  const onUpload = vi.fn();
  render(<DropZone onFilesAccepted={onUpload} isUploading={false} />);

  // Simulate file drop
  const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
  fireEvent.drop(screen.getByRole('button'), { dataTransfer: { files: [file] } });

  expect(onUpload).toHaveBeenCalledWith([file]);
});
```

## Review Process

1. All PRs require at least one approval
2. CI checks must pass
3. Code coverage should not decrease
4. Documentation must be updated if needed

## CI/CD and Docker Publishing

When a PR is merged to `main`, the **Publish Docker Images** workflow runs automatically. It builds multi-platform images and pushes them to Docker Hub and GitHub Container Registry. Maintainers must configure `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets for this to work. See [Docker Deployment](docs/getting-started/docker.md#automatic-publishing-cicd) for details.

## Getting Help

- Create an issue for questions
- Join discussions in existing issues
- Check the README for common solutions

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- README.md contributors section

Thank you for contributing to Duckling!

