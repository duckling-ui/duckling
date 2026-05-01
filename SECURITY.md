# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.0.12  | :white_check_mark:                |
| 0.0.10a  | :white_check_mark:                |
| 0.0.9  | :white_check_mark:                |
| 0.0.8  | :white_check_mark:                |
| 0.0.7  | :x:                |
| 0.0.6   | :x:                |
| 0.0.5   | :x:                |
| 0.0.3   | :x:                |
| 0.0.2   | :x:                |
| 0.0.1   | :x:                |

## Security Audit Summary

Last audit: March 3, 2026

### Product surface notes

- **2026-05-01**: Tooling only: `scripts/docker-build.sh` uses Bash parameter expansions that remain valid under `set -u` on macOS `/bin/bash` 3.2 when optional `buildx` flag arrays are empty (developer ergonomics; no change to image contents or publish gates). Pull request CI runs a **Docker build script (publish parity)** job that re-checks syntax and the same flag branches used by `publish-docker.yml` on `ubuntu-latest`.
- **2026-04-29**: Docker publish scan gate fix: backend requirements now pin `jaraco.context>=6.1.0` and `wheel>=0.46.2` to resolve Trivy-reported high vulnerabilities in Python packaging components.
- **2026-04-29**: Docker hardening update: frontend image now runs as non-root (`USER nginxuser`), production/prebuilt compose add read-only rootfs + `cap_drop: ["ALL"]` + `no-new-privileges` + scoped `tmpfs` mounts, and publish CI adds Trivy gating, Syft SBOM artifacts, provenance-enabled builds, and keyless Cosign signing.
- **2026-04-08**: Documentation only: the Quick Start guide clarifies folder drag-and-drop and folder vs **Choose files…** selection; upload endpoints and server-side validation are unchanged.
- **2026-04-08**: Documentation only: French **Features** page translation and removal of a duplicate statistics subsection in English features; no application or API change.
- **2026-04-08**: Documentation only: German and Spanish **Features**, German/French/Spanish **Configuration**, and localized home page updates (feature-card anchors, Docling link on `de`, changelog link on `es`); no application or API change.
- **2026-04-08**: Documentation only: Full localization sweep for `docs/de/`, `docs/fr/`, and `docs/es/` (API, architecture, deployment, getting started, contributing, user-guide formats/screenshots, docling index stubs, images README); stable heading anchors on localized contributing code-style pages; no application or API change.
- **2026-04-08**: Documentation only: `docs/javascripts/language-selector.js` rewrites MkDocs language dropdown URLs client-side (same-page locale switch; no change to auth or data handling).
- **2026-03-30**: The web UI upload flow was unified (removed a separate toolbar control for “batch” uploads). Conversion requests still use the same REST endpoints and server-side type/size checks; this was a client presentation change.
- **2026-03-30**: Accessibility updates: in-app dialogs use explicit accessible names; scrollable areas are keyboard-focusable where needed; export HTML preview remains sandboxed/trusted-content as documented. Published docs gain underlined content links and focusable code/table scroll wrappers via `docs/javascripts/scrollable-focus.js`.
- **2026-03-30**: Export HTML preview and embedded docs iframe use labeled regions / titles for assistive tech; preview content remains trusted, sanitized server-side output only (see XSS row below).
- **2026-03-30**: `backend/requirements.txt` pins `pymdown-extensions>=10.21.2` (with `markdown>=3.6` and `mkdocs>=1.6` so pip can resolve that stack) so `mkdocs build` does not fail on Pygments HTML formatting for code fences without a title (CI/docs supply-chain consistency, not an application exploit).

### Vulnerability Status

| Category | Status | Notes |
|----------|--------|-------|
| Backend dependency vulnerabilities | ✅ No known issues | All Python dependencies appear secure (run `pip-audit` to verify) |
| Frontend dependency vulnerabilities | ✅ Fixed | Updated vite to 7.3.1 and vitest to 4.0.18 (fixed esbuild vulnerability) |
| Flask debug mode | ✅ Fixed | Now uses environment variables |
| Path traversal | ✅ Fixed | Added path validation |
| SQL injection | ✅ Protected | Using SQLAlchemy ORM with parameterized queries |
| XSS (Cross-Site Scripting) | ⚠️ Mitigated | Uses dangerouslySetInnerHTML for trusted docs only |
| CORS | ✅ Configured | Restricted to localhost origins in development |
| Batch / folder uploads | ✅ Validated | Same extension and size rules as single uploads; unsupported parts are rejected; empty batches return 400. Whole-request limit remains `MAX_CONTENT_LENGTH`—very large folders may require multiple requests. |
| Container runtime hardening | ✅ Enforced in prod compose | Non-root runtime, read-only rootfs, no new privileges, all caps dropped, scoped writable tmpfs paths |
| Container supply chain | ✅ Gated in publish CI | Trivy high/critical gate, SBOM generation, provenance-enabled buildx publish, Cosign signing |

### Frontend Security Updates (January 2026)

**Fixed esbuild vulnerability (GHSA-67mh-4wv8-2f99)**
- **Severity**: Moderate (was)
- **Status**: ✅ **FIXED** - Updated vite to 7.3.1 and vitest to 4.0.18
- **Impact**: Was development server only - now resolved
- **Packages updated**:
  - `vite`: 5.4.21 → 7.3.1
  - `vitest`: 1.6.1 → 4.0.18
  - `@vitest/coverage-v8`: 1.6.1 → 4.0.18
  - `@vitejs/plugin-react`: 4.7.0 → 5.1.2
- **Additional updates**:
  - `@tanstack/react-query`: 5.90.12 → 5.90.20 (patch)
  - `axios`: 1.13.2 → 1.13.3 (patch)
  - `autoprefixer`: 10.4.22 → 10.4.23 (patch)
  - `eslint-plugin-react-refresh`: 0.4.24 → 0.4.26 (patch)
  - `tailwindcss`: 3.4.18 → 3.4.19 (patch)
  - `@testing-library/react`: 14.3.1 → 16.3.2 (minor)

**Fixed Rollup and Minimatch vulnerabilities (March 2026)**
- **Rollup path traversal (GHSA-mw96-cpmx-2vgc)**: Added npm override `rollup >=4.59.0` (already resolved to 4.59.0 via Vite).
- **Minimatch ReDoS (GHSA-3ppc-4f35-3m26)**: Added npm override for `@typescript-eslint/typescript-estree` to use `minimatch 9.0.6`.
- **Werkzeug safe_join Windows device names (CVE-2026-27199, GHSA-29vq-49wr-vm6x)**: Upgraded werkzeug 3.1.4 → 3.1.6 to fix multi-segment paths like `example/NUL` on Windows.
- **Flask session Vary: Cookie (CVE-2026-27205)**: Upgraded flask 3.0.0 → 3.1.3 so `Vary: Cookie` is set when session is accessed via `in` operator (e.g., `"session_id" not in session`).
- **SSRF prevention**: `validate_url_safe_for_request()` blocks loopback, private IPs, link-local, metadata endpoints. Applied to `download_from_url`, `download_from_url_with_images`, `download_image`.

## Security Measures

### Backend Security

1. **Environment-Based Configuration**
   - Debug mode disabled by default
   - Secret keys loaded from environment variables
   - Host binding defaults to localhost (127.0.0.1)

2. **Input Validation**
   - File upload validation (extension whitelist)
   - File size limits (100MB default)
   - Search query length limits and sanitization
   - URL validation for outbound requests (SSRF prevention): blocks loopback, private IPs, link-local, metadata endpoints

3. **Path Traversal Protection**
   - All file serving endpoints validate paths
   - Resolved paths checked against allowed directories
   - Directory traversal sequences blocked
   - History reload endpoints validate `job_id` with a strict allowlist and use safe join + containment checks when constructing output paths

4. **Database Security**
   - SQLAlchemy ORM prevents SQL injection
   - Parameterized queries for all database operations
   - LIKE wildcards escaped in search queries

5. **CORS Configuration**
   - Origins restricted to localhost in development
   - Configurable for production deployments

### Frontend Security

1. **Content Security**
   - Documentation rendering uses trusted backend-generated HTML
   - No user-generated content rendered as HTML

2. **API Communication**
   - All API calls use typed interfaces
   - Error responses handled gracefully

## Production Deployment Checklist

Before deploying to production, ensure:

- [ ] Set `FLASK_DEBUG=false` environment variable
- [ ] Set a strong `SECRET_KEY` environment variable
- [ ] Configure `FLASK_HOST` appropriately (not 0.0.0.0 unless behind reverse proxy)
- [ ] Update CORS origins in `backend/duckling.py` to match your domain
- [ ] Use HTTPS in production (configure via reverse proxy)
- [ ] Set appropriate `MAX_CONTENT_LENGTH` for your use case
- [ ] Review and restrict file upload extensions if needed
- [ ] Enable rate limiting (via reverse proxy or middleware)
- [ ] Set up log monitoring for security events
- [ ] Use `docker-compose.prod.yml` or `docker-compose.prebuilt.yml` hardened runtime defaults
- [ ] Verify image signatures before deployment (`cosign verify`)
- [ ] Review SBOM and vulnerability scan output for release tags

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `false` | Enable debug mode (never in production) |
| `FLASK_HOST` | `127.0.0.1` | Host to bind to |
| `FLASK_PORT` | `5001` | Port to listen on |
| `SECRET_KEY` | `dev-secret-key...` | Flask secret key (MUST change in production) |
| `MAX_CONTENT_LENGTH` | `104857600` | Max upload size in bytes (100MB) |

### CI/CD Secrets (GitHub Actions)

The Publish Docker Images workflow uses repository secrets. Never commit these:

- `DOCKERHUB_USERNAME` – Docker Hub username
- `DOCKERHUB_TOKEN` – Docker Hub access token (or password) – store as a secret, never in code

## Known Limitations

1. **XSS in Documentation Viewer**: The docs panel uses `dangerouslySetInnerHTML` to render markdown-converted HTML. This is acceptable because:
   - Documentation is served from local files only
   - No user-generated content is rendered
   - Content is converted server-side with trusted markdown library

2. **Multilingual documentation paths**: The documentation site is served under locale-prefixed paths (e.g. `/api/docs/site/en/`, `/api/docs/site/es/`). This does not change the trust model: docs are still served from local build output only.

3. **Vendored upstream documentation**: The MkDocs site includes a curated, vendored subset of upstream Docling documentation under `docs/docling/`, synced via `scripts/sync_docling_docs.py`. This content is treated as trusted project documentation (not user input) and is built into the local `site/` output.

2. **Local File Access**: The application reads and writes files to configured directories. Ensure proper filesystem permissions.

3. **No Authentication**: This application is designed for local/personal use and does not include user authentication. For multi-user deployments, add authentication via a reverse proxy or middleware.

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **Do NOT** open a public issue
2. Email the maintainers directly with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to:
- Confirm the vulnerability
- Develop a fix
- Coordinate disclosure

## Security Updates

Security updates are released as patch versions. We recommend:
- Enabling automatic dependency updates (Dependabot, Renovate)
- Subscribing to release notifications
- Regularly running `pip-audit` (or `pip3-audit`) and `npm audit`
- Reviewing and addressing vulnerabilities in both production and development dependencies

## Dependencies

### Backend (Python)

Run security audit:
```bash
cd backend
source venv/bin/activate  # or create venv: python3 -m venv venv
pip3 install pip-audit
pip-audit
```

Alternatively, use pipx:
```bash
cd backend
pipx run pip-audit
```

### Frontend (Node.js)

Run security audit:
```bash
cd frontend
npm audit
```

## Secure Development Practices

When contributing:

1. Never commit secrets or credentials
2. Use environment variables for configuration
3. Validate all user input
4. Use parameterized queries (never string concatenation for SQL)
5. Escape output appropriately for the context
6. Keep dependencies updated
7. Run security scanners before submitting PRs
