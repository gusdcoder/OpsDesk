# OpsDesk API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints (except `/auth/login`) require a JWT Bearer token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### POST /auth/login
Authenticate with email and password.

**Request:**
```json
{
  "email": "admin@opsdesk.local",
  "password": "SecurePassword123",
  "totp_code": "123456" // optional if MFA enabled
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Hosts

#### POST /hosts
Create a new host.

**Request:**
```json
{
  "hostname": "web-server-01",
  "fqdn": "web-server-01.prod.company.com",
  "ip": "192.168.1.100",
  "os": "linux",
  "environment": "prod",
  "owner": "devops-team",
  "criticality": "high",
  "tags": ["web", "production"],
  "connection_method": "bastion_ssh",
  "bastion_host": "bastion.company.com",
  "bastion_port": 22
}
```

#### GET /hosts
List all hosts with optional filters.

**Query Parameters:**
- `skip`: Offset for pagination (default: 0)
- `limit`: Results per page (default: 50, max: 100)
- `environment`: Filter by environment (prod/stage/dev)
- `os`: Filter by operating system (windows/linux/macos)
- `criticality`: Filter by criticality (critical/high/medium/low)
- `tag`: Filter by tag

#### GET /hosts/{host_id}
Get a specific host by ID.

#### PUT /hosts/{host_id}
Update a host.

#### DELETE /hosts/{host_id}
Delete a host.

#### POST /hosts/import-csv
Import hosts from CSV file.

**CSV Format:**
```
hostname,ip,fqdn,os,environment,owner,team,criticality,notes
web-01,10.0.1.10,web-01.prod.com,linux,prod,ops,platform,high,Web Server
db-01,10.0.2.10,db-01.prod.com,linux,prod,dba,platform,critical,Primary DB
```

#### POST /hosts/{host_id}/metrics:update
Trigger on-demand metrics collection from Prometheus.

**Response:**
```json
{
  "host_id": 1,
  "metrics": {
    "cpu_count": 8,
    "memory_total_gb": 16,
    "disk_total_gb": 500,
    "uptime_seconds": 2592000
  },
  "collected_at": "2024-01-15T10:30:00Z"
}
```

#### GET /hosts/{host_id}/metrics:latest
Get latest metrics snapshot for a host.

### Artifacts

#### POST /artifacts/{host_id}/artifacts
Upload an artifact file for a host.

**Form Data:**
- `file`: Binary file
- `file_type`: Type of artifact (log/config/binary/credential)

**Response:**
```json
{
  "id": 1,
  "host_id": 1,
  "name": "app.log",
  "file_type": "log",
  "size_bytes": 5242880,
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

#### GET /artifacts/{host_id}/artifacts
List artifacts for a host.

#### GET /artifacts/{artifact_id}/download
Download an artifact file.

#### DELETE /artifacts/{artifact_id}
Delete an artifact.

### Audit

#### GET /audit
List audit events with optional filters.

**Query Parameters:**
- `skip`: Offset for pagination
- `limit`: Results per page
- `action`: Filter by action type
- `entity_type`: Filter by entity type

#### GET /audit/export/csv
Export audit logs as CSV file.

### Users

#### POST /users
Create a new user (Admin only).

#### GET /users
List all users.

#### GET /users/{user_id}
Get a specific user.

#### PUT /users/{user_id}
Update a user.

#### DELETE /users/{user_id}
Delete a user.

### Settings

#### GET /settings/runtime
Get runtime configuration including dynamic port.

**Response:**
```json
{
  "runtime_port": 42345,
  "environment": "production",
  "prometheus_url": "http://prometheus:9090",
  "max_artifact_size_mb": 100
}
```

#### GET /settings/integrations
Get integration settings.

#### PUT /settings/integrations
Update integration settings.

### Health Checks

#### GET /healthz
Liveness probe.

#### GET /readyz
Readiness probe.

## Error Responses

All errors follow standard HTTP status codes:

- `400`: Bad Request
- `401`: Unauthorized (invalid or missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `409`: Conflict (resource already exists)
- `500`: Internal Server Error
- `503`: Service Unavailable

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

## Rate Limiting

Auth endpoints are rate-limited to 5 requests per minute per IP.

## Webhooks

Not currently implemented.
