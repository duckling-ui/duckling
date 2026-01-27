# Contributing to Duckling

Thank you for your interest in contributing to Duckling! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.MD), which is based on the Contributor Covenant 3.0. We are committed to providing a welcoming, safe, and inclusive environment for everyone.

Please read the full [Code of Conduct](CODE_OF_CONDUCT.MD) before contributing.

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
5. **Run tests**: Ensure all tests pass
6. **Commit with clear messages**: Follow conventional commits
7. **Push to your fork**
8. **Create a Pull Request**

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Backend Setup

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
- Mock API calls appropriately

```typescript
it('should upload file on drop', async () => {
  const onUpload = vi.fn();
  render(<DropZone onFileAccepted={onUpload} />);

  // Simulate file drop
  const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
  fireEvent.drop(screen.getByRole('button'), { dataTransfer: { files: [file] } });

  expect(onUpload).toHaveBeenCalledWith(file);
});
```

## Review Process

1. All PRs require at least one approval
2. CI checks must pass
3. Code coverage should not decrease
4. Documentation must be updated if needed

## Getting Help

- Create an issue for questions
- Join discussions in existing issues
- Check the README for common solutions

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- README.md contributors section

Thank you for contributing to Duckling!

