# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          | End of Life |
|---------|-------------------|-------------|
| 0.1.x   | Yes               | TBD         |
| < 0.1   | No                | N/A         |

## Reporting a Vulnerability

If you discover a security vulnerability in Tendos, please report it **responsibly and privately** to us.

### How to Report

Use GitHub's private vulnerability reporting flow:

- Go to the Security tab of this repository
- Click "Report a vulnerability"
- Submit the report with reproduction details

If you cannot use GitHub Security Advisories, open a minimal public issue requesting a private security contact path (without disclosing exploit details).

### What to Include

Please include:
1. Description of the vulnerability
2. Affected components or versions
3. Steps to reproduce (if applicable)
4. Impact assessment (severity, scope)
5. Suggested fix (if you have one)
6. Your contact information

### Response Timeline

- **Initial acknowledgment**: Within 48 hours
- **Status update**: Within 7 days
- **Coordinated disclosure**: Following our 90-day disclosure policy (see below)

## Disclosure Policy

We follow a 90-day coordinated disclosure process:

1. **Days 1-7**: Initial investigation and acknowledgment
2. **Days 8-60**: Development and testing of fix
3. **Days 61-90**: Final validation and preparation for release
4. **Day 90**: Public disclosure of vulnerability and release of patch

If a fix is ready before 90 days, we may disclose earlier with mutual agreement. If the issue is more complex, we may negotiate an extension with the reporter.

## Security Practices

### Dependency Management

- **Automated scanning**: Dependencies are scanned for known vulnerabilities using Dependabot
- **Regular updates**: Dependencies are updated regularly to include security patches
- **Pinned versions**: Production dependencies are pinned to specific versions

### Code Security

- **Static Analysis**: SAST tools (Ruff, mypy) are used to detect potential security issues
- **Code Review**: All code changes are reviewed for security implications
- **Vulnerability Scanning**: Regular scans of the codebase for known vulnerabilities

### Release Security

- **Signed releases**: Major releases are cryptographically signed
- **Checksum verification**: Release artifacts include checksums for verification
- **Supply chain security**: We maintain secure build and release processes

## Security Best Practices for Users

When using Tendos:

1. **Keep dependencies updated**: Regularly update Tendos and its dependencies
2. **Use trusted cartridges**: Only load cartridges from trusted sources
3. **Review permissions**: Understand what permissions cartridges request
4. **Sandbox sensitive workloads**: Run untrusted cartridges in isolated environments
5. **Report suspicious activity**: Open a GitHub issue with relevant evidence (without sharing secrets)

## Security Questions

For security-related questions that don't constitute a vulnerability report:
- Open a discussion in the repository
- Open a GitHub issue labeled `security-question` for non-sensitive inquiries

Thank you for helping keep Tendos secure!
