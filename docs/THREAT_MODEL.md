# OpsDesk Threat Model

## Assets

1. **Host Inventory**: List of managed hosts with credentials, IPs, configurations
2. **SSH Credentials/Keys**: Authentication materials for host access
3. **Telemetry Data**: System metrics (CPU, memory, disk, network)
4. **Artifacts**: Files exfiltrated from hosts (logs, configs, credentials)
5. **Audit Logs**: Historical record of all system access and modifications
6. **User Credentials**: Email/password combinations for authentication

## Threat Actors

- External attackers (no authentication)
- Malicious insiders (authenticated, wrong role)
- Compromised client (XSS injection)
- Compromised backend (code injection)
- Network attacker (MITM on HTTP)

## Threats & Mitigations

### T1: Unauthorized Host Access
**Threat**: Attacker gains access to confidential host inventory.
**Likelihood**: Medium | **Impact**: High

**Mitigations**:
- JWT authentication required on all endpoints
- Role-based access control (RBAC)
- Rate limiting on auth endpoints (5 req/min)
- Audit logging of all access
- TLS/HTTPS in production

### T2: Credential Compromise
**Threat**: Attacker intercepts SSH credentials or API tokens.
**Likelihood**: Medium | **Impact**: Critical

**Mitigations**:
- Passwords hashed with Argon2
- HTTPS/TLS for all transmission
- JWT tokens expire after 24 hours
- Optional TOTP-based MFA
- Secrets managed via environment variables

### T3: SQL Injection
**Threat**: Attacker manipulates database queries via user input.
**Likelihood**: Low | **Impact**: Critical

**Mitigations**:
- SQLAlchemy ORM prevents SQL injection
- Pydantic v2 input validation
- No raw SQL queries

### T4: Audit Log Tampering
**Threat**: Attacker modifies or deletes audit logs.
**Likelihood**: Low | **Impact**: High

**Mitigations**:
- Append-only audit logs
- Database permissions restrict access
- Regular log exports

### T5: Role Bypass
**Threat**: Operator escalates privileges to Admin.
**Likelihood**: Low | **Impact**: Critical

**Mitigations**:
- RBAC enforced server-side
- Role checked on every endpoint
- Audit log records role-based actions
