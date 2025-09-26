# Security Policy

## Supported Versions

We actively support security updates for the following versions of DomainGenChecker:

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of DomainGenChecker seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

Instead, please report security vulnerabilities using one of these methods:

1. **GitHub Security Advisories (Preferred)**
   - Go to https://github.com/srnetadmin/DomainGenCheck/security/advisories
   - Click "New draft security advisory"
   - Fill out the form with details about the vulnerability

2. **Private Email**
   - Email: srnetadmin@users.noreply.github.com
   - Subject: [SECURITY] DomainGenChecker Vulnerability Report
   - Include a detailed description of the vulnerability

### What to Include

Please include as much information as possible to help us understand and reproduce the issue:

- Type of vulnerability (e.g., injection, authentication bypass, etc.)
- Affected version(s)
- Step-by-step instructions to reproduce the issue
- Proof of concept or exploit code (if available)
- Potential impact and severity assessment
- Any suggested remediation steps

### Response Timeline

- **Initial Response**: Within 48 hours
- **Triage and Assessment**: Within 1 week
- **Fix Development**: Timeline depends on severity and complexity
- **Public Disclosure**: After fix is released and users have had time to update

### Security Update Process

1. We will confirm receipt of your report
2. We will assess the vulnerability and its impact
3. We will develop and test a fix
4. We will release a security update
5. We will publicly disclose the vulnerability details (with credit to reporter, if desired)

### Bug Bounty

While we don't currently offer a formal bug bounty program, we greatly appreciate security researchers who help keep DomainGenChecker secure. We will acknowledge your contribution in our release notes and security advisories.

## Security Best Practices for Users

When using DomainGenChecker:

1. **Keep Updated**: Always use the latest version to benefit from security fixes
2. **Validate Input**: Be cautious with domain lists from untrusted sources
3. **Network Security**: Use appropriate DNS servers and network configurations
4. **Rate Limiting**: Respect rate limits to avoid being blocked or triggering security systems
5. **Log Security**: Monitor logs for any suspicious activity when running the tool

## Scope

This security policy applies to:

- The main DomainGenChecker application code
- Official distribution packages
- Documentation and examples
- CI/CD pipelines and build processes

Third-party dependencies are covered by their respective security policies, but we will coordinate fixes for vulnerabilities that affect DomainGenChecker users.

## Contact

For non-security related issues, please use the normal GitHub issue tracker.

For security matters, use the methods outlined above.

---

Thank you for helping keep DomainGenChecker and its users secure!