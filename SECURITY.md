# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in RandomCoffeeBot, please
open a GitHub issue with the label **security**. Avoid disclosing
sensitive details publicly until the issue has been addressed.

For critical vulnerabilities, contact the maintainer directly.

## Supported Versions

Only the latest release on the `master` branch receives security fixes.

## Security Best Practices

- Never commit `.env` files or secrets to version control
- Use a strong, randomly generated `SECRET_KEY` in production
  (`openssl rand -hex 32`)
- Rotate credentials regularly
- Use separate credentials for development, staging, and production
- Restrict database access to application containers only
- Keep dependencies up to date (Dependabot alerts are monitored)
- Review pre-commit hooks and CI checks before merging
