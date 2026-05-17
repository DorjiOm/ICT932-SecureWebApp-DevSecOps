# System Architecture — ICT932 Secure Web Application

## Overview

The application is a Django-based Task Manager with security integrated at every layer. It follows a standard MVC pattern with additional security middleware and logging.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      Browser / Client                    │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────┐
│                   Django Application                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   accounts/  │  │    tasks/    │  │  taskmanager/ │  │
│  │  - Login     │  │  - Task CRUD │  │  - Settings   │  │
│  │  - Register  │  │  - Task List │  │  - URLs       │  │
│  │  - 2FA       │  │  - Complete  │  │  - WSGI       │  │
│  │  - RBAC      │  │  - Delete    │  └───────────────┘  │
│  └──────────────┘  └──────────────┘                     │
│                                                          │
│  Security Middleware:                                    │
│  - CSRF Protection                                       │
│  - XFrame Options                                        │
│  - Security Headers                                      │
│  - Session Management                                    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   SQLite Database                        │
│  - Users table (hashed passwords)                        │
│  - Profile table (roles)                                 │
│  - Tasks table (user-scoped)                             │
│  - TOTP devices (2FA secrets)                            │
└─────────────────────────────────────────────────────────┘
```

## Security Layers

### Layer 1 — Authentication
- Django built-in auth with PBKDF2 password hashing
- Brute force protection via cache-based attempt tracking
- Account lockout after 5 failed attempts (5 minute cooldown)

### Layer 2 — Authorisation (RBAC)
- Two roles: Admin and User
- Profile model extends Django User with role field
- All views decorated with @login_required
- Admin views check profile.is_admin() before rendering

### Layer 3 — Two-Factor Authentication
- TOTP-based 2FA using django-otp
- QR code generated for Google Authenticator setup
- Session flag otp_verified set after successful verification

### Layer 4 — Input Validation
- Django forms provide server-side validation
- XSS prevention via Django's auto-escaping in templates
- Manual escape() calls on raw POST data in task views
- Priority field whitelisted to allowed values only

### Layer 5 — Logging
- Python logging module configured for security events
- Logs: registrations, logins, logouts, failed attempts, lockouts, 2FA events
- Written to security.log file
