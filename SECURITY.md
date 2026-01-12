# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within RandomCoffeeBot, please follow these steps:

### Where to Report

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please report security issues by emailing the maintainers directly or by using GitHub's private vulnerability reporting feature:

1. Go to the [Security tab](../../security/advisories/new) of this repository
2. Click "Report a vulnerability"
3. Provide detailed information about the vulnerability

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., SQL injection, XSS, authentication bypass)
- Full paths of source file(s) related to the manifestation of the issue
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-30 days
  - Medium: 30-90 days
  - Low: Next release cycle

### Disclosure Policy

- We follow coordinated disclosure
- Security patches will be released as soon as possible
- We will credit reporters in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices

When deploying RandomCoffeeBot in production:

### Environment Variables
- ✅ Always use strong, randomly generated values for `SECRET_KEY`
- ✅ Never commit `.env` files to version control
- ✅ Rotate credentials regularly
- ✅ Use separate credentials for dev/staging/production

### Database
- ✅ Use strong passwords for PostgreSQL
- ✅ Restrict database access to application containers only
- ✅ Enable SSL/TLS for database connections in production
- ✅ Regularly backup your database

### Network
- ✅ Use firewall rules to restrict access
- ✅ Only expose necessary ports
- ✅ Use reverse proxy (nginx) in production
- ✅ Enable HTTPS for any HTTP endpoints

### Docker
- ✅ Don't expose ports publicly (use `127.0.0.1:port:port`)
- ✅ Scan images for vulnerabilities regularly
- ✅ Keep base images up to date
- ✅ Use Docker secrets for sensitive data in Swarm/K8s

### Dependencies
- ✅ Keep dependencies up to date
- ✅ Review Dependabot alerts promptly
- ✅ Use `uv` lock file to ensure reproducible builds

### Monitoring
- ✅ Monitor logs for suspicious activity
- ✅ Set up alerting for errors and anomalies
- ✅ Regularly review access logs

## Known Security Considerations

### Rate Limiting
The application includes rate limiting via `ThrottlingMiddleware` to prevent abuse. Ensure Redis is properly configured and accessible.

### SQL Injection
All database queries use SQLAlchemy ORM, which provides protection against SQL injection by default. Avoid raw SQL queries.

### Input Validation
User inputs are validated using Pydantic schemas. Never bypass validation.

## Security Updates

Security updates will be announced via:
- GitHub Security Advisories
- Release notes in CHANGELOG.md
- GitHub releases

Subscribe to repository notifications to stay informed.

## Hall of Fame

We thank the following security researchers for responsibly disclosing vulnerabilities:

<!-- Add names here when vulnerabilities are reported and fixed -->

---

Last updated: 2026-01-12
