# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Security Audit Summary

Last audit: December 2024

### Vulnerability Status

| Category | Status | Notes |
|----------|--------|-------|
| Dependency vulnerabilities | ✅ Fixed | Updated flask-cors, gunicorn, werkzeug |
| Flask debug mode | ✅ Fixed | Now uses environment variables |
| Path traversal | ✅ Fixed | Added path validation |
| SQL injection | ✅ Protected | Using SQLAlchemy ORM with parameterized queries |
| XSS (Cross-Site Scripting) | ⚠️ Mitigated | Uses dangerouslySetInnerHTML for trusted docs only |
| CORS | ✅ Configured | Restricted to localhost origins in development |

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

3. **Path Traversal Protection**
   - All file serving endpoints validate paths
   - Resolved paths checked against allowed directories
   - Directory traversal sequences blocked

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
- [ ] Update CORS origins in `backend/app.py` to match your domain
- [ ] Use HTTPS in production (configure via reverse proxy)
- [ ] Set appropriate `MAX_CONTENT_LENGTH` for your use case
- [ ] Review and restrict file upload extensions if needed
- [ ] Enable rate limiting (via reverse proxy or middleware)
- [ ] Set up log monitoring for security events

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `false` | Enable debug mode (never in production) |
| `FLASK_HOST` | `127.0.0.1` | Host to bind to |
| `FLASK_PORT` | `5001` | Port to listen on |
| `SECRET_KEY` | `dev-secret-key...` | Flask secret key (MUST change in production) |
| `MAX_CONTENT_LENGTH` | `104857600` | Max upload size in bytes (100MB) |

## Known Limitations

1. **XSS in Documentation Viewer**: The docs panel uses `dangerouslySetInnerHTML` to render markdown-converted HTML. This is acceptable because:
   - Documentation is served from local files only
   - No user-generated content is rendered
   - Content is converted server-side with trusted markdown library

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
- Regularly running `pip-audit` and `npm audit`

## Dependencies

### Backend (Python)

Run security audit:
```bash
cd backend
source venv/bin/activate
pip-audit
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
