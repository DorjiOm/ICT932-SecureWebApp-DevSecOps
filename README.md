# ICT932 — Secure Web Application with DevSecOps Pipeline

A secure Django-based Task Manager application built using DevSecOps principles for ICT932 Cybersecurity Testing and Assurance.

---

## Team Members

| Name | Student ID | Role |
|---|---|---|
| Sweta Manandhar | CIHE240378 | Project Lead & DevSecOps Pipeline |
| Prasanna Shrestha | — | Secure App Developer |
| Dorji Om | CIHE240914 | Security Testing (SAST/DAST) |
| Deepa Gurung | CIHE240485 | Report & Documentation |

---

## Project Overview

This project is a secure task management web application that demonstrates real-world DevSecOps practices. Security is integrated at every stage — from secure coding and RBAC to automated CI/CD security scanning.

### Security Features Implemented
- Secure login and registration (Django Auth)
- Role-Based Access Control (Admin vs User)
- Two-Factor Authentication (2FA) with Google Authenticator (TOTP)
- Brute force protection (account lockout after 5 failed attempts)
- XSS prevention (input sanitization and escaping)
- CSRF protection (Django middleware)
- Security event logging
- Input validation on all forms

---

## Repository Structure

```
/
├── .github/workflows/     # CI/CD pipeline (GitHub Actions)
├── src/                   # Django application source code
│   ├── accounts/          # Authentication, RBAC, 2FA
│   ├── tasks/             # Task manager features
│   ├── taskmanager/       # Django project settings
│   └── manage.py
├── docs/                  # Project documentation
│   ├── architecture.md    # System architecture
│   ├── threat-model.md    # Threat modelling
│   └── incident-response.md
├── tests/                 # Test files
│   ├── test_auth.py       # Authentication tests
│   ├── test_tasks.py      # Task feature tests
│   └── test_security.py   # Security-specific tests
├── ci-cd/                 # Pipeline documentation
│   └── pipeline-guide.md
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.12+
- pip
- Git

### Step 1 — Clone the repository
```bash
git clone https://github.com/Swetamdhr/ICT932-SecureWebApp-DevSecOps.git
cd ICT932-SecureWebApp-DevSecOps
```

### Step 2 — Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r src/requirements.txt
pip install django-otp qrcode pillow
```

### Step 4 — Run database migrations
```bash
cd src
python manage.py migrate
```

### Step 5 — Create a superuser (admin account)
```bash
python manage.py createsuperuser
```

### Step 6 — Run the development server
```bash
python manage.py runserver
```

### Step 7 — Open the app
Go to `http://127.0.0.1:8000` in your browser.

---

## Running Tests

```bash
cd src
python manage.py test --verbosity=2
```

---

## CI/CD Pipeline

The GitHub Actions pipeline runs automatically on every push to `main` or `develop`. It includes four stages:

| Stage | Tool | Purpose |
|---|---|---|
| Build & Test | Django test runner | Unit tests |
| SAST Scan | Bandit + Safety | Static code analysis + dependency check |
| Web Scan | Nikto | Web server vulnerability scan |
| DAST Scan | OWASP ZAP | Dynamic application security testing |

---

## Security Tools Used

- **Bandit** — Python static analysis for security issues
- **Safety** — Checks Python dependencies for known vulnerabilities
- **Nikto** — Web server scanner
- **OWASP ZAP** — Dynamic application security testing

---

## OWASP Top 10 Coverage

| OWASP Category | Implementation |
|---|---|
| A01 Broken Access Control | RBAC enforced on all views |
| A02 Cryptographic Failures | Passwords hashed with PBKDF2 |
| A03 Injection | Input validation and ORM usage |
| A04 Insecure Design | Threat modelling documented |
| A07 Auth Failures | Brute force protection, 2FA |
| A09 Logging Failures | Security event logging implemented |
