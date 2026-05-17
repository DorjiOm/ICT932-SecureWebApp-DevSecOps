# CI/CD Pipeline Guide — ICT932 DevSecOps

## Overview

This project uses GitHub Actions for its CI/CD pipeline. The pipeline runs automatically on every push to `main` or `develop` and on all pull requests to `main`.

---

## Pipeline Architecture

```
Push to main/develop
        │
        ▼
┌─────────────────┐
│  Stage 1        │
│  Build & Test   │ ← Django unit tests must pass
└────────┬────────┘
         │ (on success)
    ┌────┴────┬──────────────┐
    ▼         ▼              ▼
┌────────┐ ┌────────┐  ┌──────────┐
│Stage 2 │ │Stage 3 │  │ Stage 4  │
│  SAST  │ │ Nikto  │  │ OWASP    │
│Bandit  │ │  Scan  │  │ ZAP DAST │
│Safety  │ │        │  │          │
└────┬───┘ └────────┘  └──────────┘
     │ (on success)
     ▼
┌─────────────────┐
│  Stage 5        │
│Pipeline Complete│
└─────────────────┘
```

---

## Stages Explained

### Stage 1 — Build & Unit Tests
- Sets up Python 3.12
- Installs all dependencies
- Runs Django migrations
- Runs all unit tests with `python manage.py test`
- **Pipeline stops here if tests fail**

### Stage 2 — SAST Scan
- **Bandit**: Scans Python source code for security issues
  - Checks for hardcoded passwords, SQL injection risks, dangerous functions
  - Output saved as `bandit-report.txt` artifact
- **Safety**: Checks all pip dependencies against known CVE database
  - Flags any vulnerable library versions

### Stage 3 — Nikto Web Scan
- Starts the Django development server
- Runs Nikto against `http://127.0.0.1:8000`
- Checks for: outdated software, missing security headers, dangerous files, server misconfiguration
- Output saved as `nikto-report.txt` artifact
- `continue-on-error: true` so pipeline doesn't fail on findings

### Stage 4 — OWASP ZAP DAST Scan
- Starts the Django development server
- Runs ZAP baseline scan against the running application
- Tests for OWASP Top 10 vulnerabilities dynamically
- `continue-on-error: true` so pipeline doesn't fail on findings

### Stage 5 — Pipeline Complete
- Summary of all stages run
- Only runs if Stages 1 and 2 pass

---

## Viewing Results

1. Go to your GitHub repository
2. Click **Actions** tab
3. Click on any workflow run
4. Download artifacts (bandit-report, nikto-report) from the bottom of the page

---

## Tools Reference

| Tool | Type | What it checks |
|---|---|---|
| Django test runner | Unit testing | Application logic |
| Bandit | SAST | Python code security issues |
| Safety | Dependency scan | Known CVEs in pip packages |
| Nikto | Web scan | Server-level vulnerabilities |
| OWASP ZAP | DAST | Runtime application vulnerabilities |
