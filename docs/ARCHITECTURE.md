# OpsDesk Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browsers                             │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS/HTTP
┌────────────────▼────────────────────────────────────────────────┐
│                     Frontend (Next.js)                           │
│  - React Components (Dashboard, Hosts, Artifacts, Audit)        │
│  - API Client (Axios with JWT interceptors)                     │
│  - State Management (TanStack Query)                            │
└────────────────┬────────────────────────────────────────────────┘
                 │ JSON/REST
┌────────────────▼────────────────────────────────────────────────┐
│                  Backend (FastAPI)                              │
│  - Auth Router (JWT, MFA, TOTP)                                 │
│  - Hosts Router (CRUD, CSV Import)                              │
│  - Metrics Router (Prometheus queries)                          │
│  - Artifacts Router (Upload/Download)                          │
│  - Audit Router (Logging, Exports)                             │
│  - Users Router (RBAC Management)                              │
│  - Settings Router (Configuration)                             │
└────────────────┬────────────────────────────────────────────────┘
                 │ SQL
┌────────────────▼────────────────────────────────────────────────┐
│                  Database (PostgreSQL)                          │
│  - Users (email, role, MFA)                                     │
│  - Hosts (inventory, connection details)                       │
│  - Artifacts (file metadata)                                    │
│  - Audit Events (append-only logs)                             │
│  - Metrics Snapshots (TTL-based)                               │
│  - Settings (configuration store)                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  External Services                                              │
│  - Prometheus (metrics queries)                                 │
│  - SSH Bastions (command templates)                            │
│  - Remote Hosts (data collection targets)                      │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Host Metrics Collection

1. User clicks "Update Metrics" on host detail page
2. Frontend sends POST to `/hosts/{host_id}/metrics:update`
3. Backend queries Prometheus for host metrics
4. Metrics stored in `metrics_snapshots` table with TTL
5. Response returned with latest data
6. Frontend displays metrics or "Last Updated by X at Y" badge

### SSH Command Generation

1. User views host detail page
2. "Copy SSH Command" button uses `ssh_template`
3. Template substitutes `{{user}}`, `{{host}}`, `{{port}}`, `{{bastion}}`
4. Command copied to clipboard
5. Audit log records "SSH_COMMAND_COPIED" event

### Artifact Upload

1. User uploads file on host artifacts tab
2. File streamed to `/artifacts/{host_id}/artifacts`
3. Server stores in `artifact_storage_path` with UUID filename
4. Metadata persisted to `artifacts` table
5. Audit log records upload event
6. File accessible via `/artifacts/{artifact_id}/download`

## Security Layers

### Authentication
- Email + Argon2 hashed passwords
- JWT tokens with configurable expiration
- Optional TOTP-based MFA
- Token refresh mechanism

### Authorization (RBAC)
- **Admin**: Full system access
- **Operator**: Manage hosts, trigger updates, upload artifacts
- **Auditor**: Read-only + audit log access
- **Viewer**: Read-only basic access

### Data Protection
- HTTPS in production
- CORS configured to allowed origins
- CSRF tokens on state-changing endpoints
- Rate limiting on auth endpoints
- Audit trail for all operations
- Append-only audit logs

## Deployment Architecture

### Docker Compose (Local/Development)
```
opsdesk-net
├─ postgres (PostgreSQL 16)
├─ backend (FastAPI + Uvicorn)
└─ frontend (Next.js)
```

### Production Deployment (Reference)
```
LoadBalancer/Reverse Proxy
├─ Frontend Service (Next.js, horizontal scale)
├─ Backend Service (FastAPI, horizontal scale)
└─ Database (PostgreSQL, managed/HA)
```

## File Storage

**Location**: `/artifacts` (mounted volume in Docker)

**Structure**:
```
/artifacts/
├─ host_1/
│  ├─ uuid1.log
│  ├─ uuid2.zip
│  └─ uuid3.conf
├─ host_2/
│  └─ uuid4.bin
└─ ...
```

**Retention**: TTL-based cleanup of metrics snapshots (configurable)

## Performance Considerations

1. **Pagination**: All list endpoints paginate (limit: 100)
2. **Indexes**: Key columns indexed (email, hostname, ip, etc.)
3. **TTL Cleanup**: Metrics snapshots auto-expire
4. **File Uploads**: Chunk-based streaming
5. **Query Optimization**: N+1 query prevention via SQLAlchemy relationships

## Monitoring & Observability

### Health Checks
- `/healthz`: Liveness (always returns 200)
- `/readyz`: Readiness (checks database connectivity)

### Logging
- Structured JSON logs via `structlog`
- Log levels: DEBUG (dev), INFO (default), WARN, ERROR
- Audit middleware logs all HTTP requests

### Metrics
- Host metrics queried on-demand from Prometheus
- No automatic polling to reduce load
