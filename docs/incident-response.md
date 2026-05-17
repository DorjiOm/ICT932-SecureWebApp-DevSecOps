# Incident Response Simulation — ICT932

## Simulated Incident: Brute Force Attack on Login

### Scenario
An attacker attempts a brute force attack against a known username, making repeated login attempts with different passwords to gain unauthorised access.

---

## Incident Timeline

| Time | Event |
|---|---|
| T+0:00 | Attacker begins sending POST requests to /login/ with correct username, wrong passwords |
| T+0:01 | Attempt 1 — Failed. Cache records 1 attempt for username/IP combination |
| T+0:02 | Attempt 2 — Failed. Cache records 2 attempts |
| T+0:03 | Attempt 3 — Failed. Cache records 3 attempts. User warned: "2 attempts remaining" |
| T+0:04 | Attempt 4 — Failed. Cache records 4 attempts. User warned: "1 attempt remaining" |
| T+0:05 | Attempt 5 — Failed. Cache records 5 attempts. Account locked for 5 minutes |
| T+0:06 | Attempt 6 — Rejected immediately. Message: "Account locked due to too many failed attempts" |
| T+5:00 | Lockout expires. Cache entry cleared automatically |

---

## Detection

The following security log entries are generated during the attack:

```
WARNING 2026-05-10 08:01:23 security Failed login attempt: testuser from IP 192.168.1.100 - 1 attempts
WARNING 2026-05-10 08:01:45 security Failed login attempt: testuser from IP 192.168.1.100 - 2 attempts
WARNING 2026-05-10 08:02:10 security Failed login attempt: testuser from IP 192.168.1.100 - 3 attempts
WARNING 2026-05-10 08:02:34 security Failed login attempt: testuser from IP 192.168.1.100 - 4 attempts
WARNING 2026-05-10 08:02:58 security Failed login attempt: testuser from IP 192.168.1.100 - 5 attempts
WARNING 2026-05-10 08:03:12 security Account locked: testuser from IP 192.168.1.100 - too many failed attempts
```

---

## Response Steps

### Step 1 — Detection
Security logs are monitored for repeated WARNING entries from the same IP address. Five or more failed attempts within a 5-minute window triggers an alert.

### Step 2 — Containment
The application automatically locks the account for 5 minutes via the Django cache mechanism. No manual intervention required for this first layer.

### Step 3 — Analysis
Review security.log to identify:
- The targeted username
- The attacker's IP address
- The time window of the attack

### Step 4 — Eradication
If the attack is sustained, the IP address should be blocked at the network/firewall level. For a production system this would be handled by a WAF or rate limiting proxy.

### Step 5 — Recovery
After 5 minutes the account automatically unlocks. The legitimate user can log in normally. If their account was compromised, force a password reset.

### Step 6 — Post-Incident Review
Document the incident, review logs, and consider:
- Reducing lockout threshold
- Implementing IP-based rate limiting
- Adding CAPTCHA after 3 failed attempts
- Setting up real-time alerting on repeated failures

---

## Lessons Learned

This simulation demonstrated that the brute force protection works as designed. The account locks automatically and the security log provides a clear audit trail. For a production deployment, we would add real-time alerting and IP-level blocking to complement the application-level protection.
