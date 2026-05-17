\# Security Policy



\## Reporting a Vulnerability

If you discover a security vulnerability, please open a GitHub issue.



\## Security Fixes Applied

The following vulnerabilities were identified and remediated:



| Issue | Severity | Fix Applied |

|-------|----------|-------------|

| Django 6.0.4 CVEs (3 issues) | High | Upgraded to Django 6.0.5 |

| Hardcoded SECRET\_KEY | Medium | Moved to .env file via python-decouple |

| Missing CSP header (OWASP ZAP) | Medium | Added CSP\_DEFAULT\_SRC settings |

| Cookie HttpOnly flag missing | Low | Added CSRF\_COOKIE\_HTTPONLY = True |

| Homepage 404 error | Low | Added redirect to login page |



\## Security Tools Used

\- \*\*Bandit\*\* — Python SAST scanning

\- \*\*SonarQube\*\* — Code quality and vulnerability analysis  

\- \*\*OWASP ZAP\*\* — Dynamic web application scanning

\- \*\*pip-audit\*\* — Dependency vulnerability scanning

