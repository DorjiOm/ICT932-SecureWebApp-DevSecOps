# Threat Model — ICT932 Secure Web Application

## Methodology: STRIDE

We used the STRIDE threat modelling framework to identify potential threats against the application.

---

## Assets to Protect

| Asset | Sensitivity | Impact if Compromised |
|---|---|---|
| User passwords | Critical | Account takeover |
| 2FA secrets (TOTP) | Critical | 2FA bypass |
| Task data | Medium | Data breach, privacy |
| Admin access | High | Full system compromise |
| Session tokens | High | Session hijacking |

---

## STRIDE Threat Analysis

### S — Spoofing Identity
**Threat:** Attacker impersonates a legitimate user by guessing or stealing credentials.
**Mitigation:** Brute force protection (lockout after 5 attempts), 2FA required, PBKDF2 password hashing.

### T — Tampering with Data
**Threat:** Attacker modifies task data belonging to another user by manipulating request parameters.
**Mitigation:** All task queries filtered by `user=request.user`. Object-level authorisation enforced via `get_object_or_404(Task, pk=pk, user=request.user)`.

### R — Repudiation
**Threat:** User denies performing an action (e.g., creating or deleting a task).
**Mitigation:** Security event logging captures all login, logout, task, and admin events with timestamps and IP addresses.

### I — Information Disclosure
**Threat:** Attacker reads another user's tasks or admin data.
**Mitigation:** RBAC enforced on all views. Task queries always scoped to the authenticated user. Admin dashboard restricted to admin role only.

### D — Denial of Service
**Threat:** Attacker floods the login endpoint to lock out legitimate users or exhaust server resources.
**Mitigation:** Rate limiting via Django cache. Account lockout implemented with 5-minute cooldown per username/IP combination.

### E — Elevation of Privilege
**Threat:** Regular user accesses admin-only functionality by manipulating requests.
**Mitigation:** Admin views explicitly check `request.user.profile.is_admin()`. Unauthorised attempts are logged and redirected.

---

## Attack Vector Summary

| Attack Vector | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Brute force login | High | High | Lockout after 5 attempts |
| Session hijacking | Medium | High | Secure session cookies, HTTPS |
| XSS injection | Medium | Medium | Input escaping, Django auto-escape |
| CSRF attacks | Medium | High | Django CSRF middleware |
| SQL injection | Low | Critical | Django ORM (parameterised queries) |
| 2FA bypass | Low | Critical | TOTP verification required |
| Privilege escalation | Low | High | Role checks on all admin views |

---

## Residual Risks

- **No HTTPS in development** — production deployment should enforce HTTPS
- **SQLite in use** — acceptable for prototype, should use PostgreSQL in production
- **DEBUG=True** — must be set to False before production deployment
- **Secret key in settings** — should be moved to environment variable
