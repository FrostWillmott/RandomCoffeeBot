# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in RandomCoffeeBot, please
open a GitHub issue with the label **security**. Avoid disclosing
sensitive details publicly until the issue has been addressed.

For critical vulnerabilities, contact the maintainer directly.

## Supported Versions

Only the latest release on the `master` branch receives security fixes.

## Security Best Practices

### Environment & Secrets
- Never commit `.env` files or secrets to version control
- Rotate credentials regularly
- Use separate credentials for development, staging, and production

### Database
- Use strong passwords for PostgreSQL
- Restrict database access to application containers only
- Enable SSL/TLS for database connections in production
- Back up the database regularly

### Network & Docker
- Use firewall rules to restrict access
- Don't expose ports publicly (bind to `127.0.0.1`)
- Use a reverse proxy (e.g. nginx) in production
- Scan images for vulnerabilities regularly
- Keep base images up to date

### Monitoring & Updates
- Monitor logs for suspicious activity (`LOG_FORMAT=json` in production)
- Set up alerting for errors and anomalies
- Keep dependencies up to date (Dependabot alerts are monitored)
- Review pre-commit hooks and CI checks before merging
