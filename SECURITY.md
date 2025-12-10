# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### Do NOT

- Open a public GitHub issue
- Disclose the vulnerability publicly before it's fixed

### Do

1. **Email us** at security@example.com (replace with actual email)
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Fix timeline**: Depends on severity (see below)

### Severity Levels

| Severity | Description | Fix Timeline |
|----------|-------------|--------------|
| Critical | Remote code execution, data breach | 24-48 hours |
| High | Authentication bypass, privilege escalation | 7 days |
| Medium | XSS, CSRF, information disclosure | 14 days |
| Low | Minor issues, hardening | 30 days |

## Security Measures

### File Upload Security

- **File type validation**: Only allowed extensions are accepted
- **File size limits**: Default 100MB maximum
- **Filename sanitization**: Prevents path traversal attacks
- **Temporary storage**: Uploaded files are stored temporarily and cleaned up

### API Security

- **CORS configuration**: Restricted to allowed origins
- **Input validation**: All inputs are validated
- **Error handling**: Sensitive information is not leaked in errors

### Data Storage

- **Local storage**: Files and database stored locally
- **No external transmission**: Documents are processed locally
- **Automatic cleanup**: Old files are periodically removed

## Security Best Practices for Deployment

### Production Checklist

1. **Change default secret key**:
   ```env
   SECRET_KEY=your-secure-random-key
   ```

2. **Disable debug mode**:
   ```env
   DEBUG=False
   FLASK_ENV=production
   ```

3. **Use HTTPS**: Always use TLS in production

4. **Set appropriate file limits**:
   ```env
   MAX_CONTENT_LENGTH=52428800  # 50MB
   ```

5. **Regular updates**: Keep dependencies updated

6. **Access control**: Implement authentication if needed

7. **Logging**: Enable and monitor access logs

8. **Firewall**: Restrict access to necessary ports only

### Docker Security

- Use non-root user in containers
- Scan images for vulnerabilities
- Keep base images updated
- Use read-only file systems where possible

## Known Limitations

1. **No built-in authentication**: Add authentication for multi-user deployments
2. **Local file storage**: Consider encrypted storage for sensitive documents
3. **No rate limiting**: Implement rate limiting for public deployments

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1) and announced through:

- GitHub Security Advisories
- CHANGELOG.md
- Release notes

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who report valid vulnerabilities (with their permission).

## Contact

For security concerns, contact: security@example.com

For general questions, use GitHub Issues.

