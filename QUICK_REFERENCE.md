# OpsDesk Quick Reference

## Key Features at a Glance

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Host Inventory** | CRUD hosts, tags, filters | Track all managed infrastructure |
| **SSH Management** | Template-based commands, no terminal | Generate secure access commands |
| **On-Demand Metrics** | Manual Prometheus queries | Check real-time system status |
| **Artifacts** | Upload/download files per host | Collect logs, configs, credentials |
| **RBAC** | 4 roles with granular permissions | Enforce least privilege access |
| **Audit Logging** | Append-only event trail | Track all user actions |
| **CSV Import** | Bulk host creation | Migrate from spreadsheets |
| **MFA Support** | Optional TOTP authentication | Enhance account security |

## API Quick Start

### Authentication

```bash
# Get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@opsdesk.local","password":"SecurePassword123"}'

# Use token in requests
curl http://localhost:8000/hosts \
  -H "Authorization: Bearer <token>"
```

### Common Operations

```bash
# List hosts
GET /hosts?environment=prod&limit=50

# Create host
POST /hosts
{
  "hostname": "web-01",
  "ip": "10.0.1.10",
  "os": "linux",
  "environment": "prod"
}

# Get metrics
POST /hosts/1/metrics:update

# Upload artifact
POST /artifacts/1/artifacts
  -F "file=@app.log" \
  -F "file_type=log"

# View audit logs
GET /audit?action=HOST_CREATED&limit=100
```

## Roles & Permissions

| Action | Admin | Operator | Auditor | Viewer |
|--------|-------|----------|---------|--------|
| View Hosts | ✅ | ✅ | ✅ | ✅ |
| Create/Update/Delete Hosts | ✅ | ✅ | ❌ | ❌ |
| Trigger Metrics | ✅ | ✅ | ❌ | ❌ |
| Upload Artifacts | ✅ | ✅ | ❌ | ❌ |
| Download Artifacts | ✅ | ✅ | ❌ | ❌ |
| View Audit Logs | ✅ | ❌ | ✅ | ❌ |
| Export Audit Logs | ✅ | ❌ | ✅ | ❌ |
| Manage Users | ✅ | ❌ | ❌ | ❌ |
| Configure Settings | ✅ | ❌ | ❌ | ❌ |

## Important Endpoints

| Endpoint | Method | Purpose |
|----------|--------|----------|
| `/auth/login` | POST | User authentication |
| `/auth/logout` | POST | User logout |
| `/hosts` | GET | List all hosts |
| `/hosts` | POST | Create host |
| `/hosts/{id}` | GET | Get host details |
| `/hosts/{id}/metrics:update` | POST | Collect metrics |
| `/artifacts/{host_id}/artifacts` | POST | Upload file |
| `/artifacts/{host_id}/artifacts` | GET | List files |
| `/audit` | GET | View audit logs |
| `/users` | GET | List users |
| `/settings/runtime` | GET | Runtime config |
| `/healthz` | GET | Liveness check |
| `/readyz` | GET | Readiness check |

## Environment Variables

```bash
# Required
DATABASE_URL=postgresql://...
JWT_SECRET=min-32-character-secret

# Important
PROMETHEUS_URL=http://prometheus:9090
ENVIRONMENT=production|development
ADMIN_EMAIL=admin@opsdesk.local
ADMIN_PASSWORD=SecurePassword123

# Optional
JWT_EXPIRATION_HOURS=24
MAX_ARTIFACT_SIZE_MB=100
LOG_LEVEL=info|debug
CORS_ORIGINS=["https://opsdesk.example.com"]
```

## Database Schema Summary

- **users**: Email, role, MFA settings
- **hosts**: Inventory (hostname, IP, OS, templates)
- **artifacts**: File uploads (name, type, size, path)
- **audit_events**: Append-only action log
- **metrics_snapshots**: TTL-based metric storage
- **settings**: Key-value configuration

## Troubleshooting Tips

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check token expiration, re-login |
| 403 Forbidden | Verify user role has permission |
| 404 Not Found | Verify resource ID exists |
| 413 File Too Large | Check MAX_ARTIFACT_SIZE_MB setting |
| Database Connection Error | Verify DATABASE_URL, check PostgreSQL status |
| Metrics Empty | Configure PROMETHEUS_URL, check Prometheus accessibility |
| Slow Queries | Check database indexes, review query logs |

## Security Checklist

- [ ] JWT_SECRET is long and random (32+ chars)
- [ ] Database password is strong
- [ ] HTTPS/TLS enabled in production
- [ ] CORS_ORIGINS restricted to known domains
- [ ] Audit logging reviewed regularly
- [ ] Backups tested and documented
- [ ] Firewall rules restrict database access
- [ ] SSH templates use least-privilege principles
- [ ] MFA enabled for admin accounts
- [ ] Rate limiting configured

## Performance Optimization

- Use connection pooling for database
- Index frequently filtered columns
- Implement caching for metrics
- Paginate large result sets (limit: 100)
- Monitor slow query logs
- Scale horizontally: frontend and backend are stateless
- Scale database separately: consider read replicas
