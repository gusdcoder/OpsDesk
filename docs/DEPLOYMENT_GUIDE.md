# OpsDesk Deployment Guide

## Production Deployment Architecture

```
┌─────────────────────────────────────┐
│     User Browsers (HTTPS)           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Load Balancer (e.g., nginx)       │
│   - SSL/TLS termination             │
│   - Rate limiting                   │
└──┬──────────────────────┬───────────┘
   │                      │
   │ HTTP                 │ HTTP
┌──▼─────────────┐  ┌────▼──────────┐
│   Frontend 1   │  │  Frontend 2    │
│  (Next.js)     │  │  (Next.js)     │
└────────────────┘  └────────────────┘
   │                      │
   └──────────┬───────────┘
              │ HTTP
    ┌─────────▼──────────┐
    │  Backend LB/Proxy  │
    │  (reverse proxy)   │
    └────┬──────────┬────┘
         │          │
   ┌─────▼───┐┌────▼─────┐
   │Backend 1││Backend 2 │
   │FastAPI  ││FastAPI   │
   └────┬────┘└────┬─────┘
        │          │
        └────┬─────┘
             │
        ┌────▼────────────────┐
        │  PostgreSQL (HA)    │
        │  - Master/Replica   │
        │  - Automated backup │
        └─────────────────────┘
```

## Pre-Deployment Checklist

### Security

- [ ] Change all default passwords
- [ ] Generate strong JWT_SECRET (min 32 chars)
- [ ] Enable TLS/SSL certificates
- [ ] Configure HTTPS only
- [ ] Set up firewall rules
- [ ] Configure VPC/security groups
- [ ] Enable audit logging
- [ ] Set up log aggregation
- [ ] Enable database encryption
- [ ] Review CORS origins

### Infrastructure

- [ ] Database: PostgreSQL 16+ with HA setup
- [ ] Object storage: For artifact backups (S3/GCS/Azure Blob)
- [ ] Secrets management: Use AWS Secrets Manager / HashiCorp Vault
- [ ] Monitoring: Prometheus + Grafana
- [ ] Logging: ELK Stack / Splunk
- [ ] Backup strategy: Daily incremental + weekly full
- [ ] Disaster recovery plan documented
- [ ] Load balancer configured
- [ ] CDN for static assets (optional)

### Performance

- [ ] Connection pooling tuned
- [ ] Caching strategy implemented
- [ ] Static assets optimized
- [ ] Database indexes created
- [ ] Query performance reviewed

## Environment Setup

### Production .env

```bash
# Database
DATABASE_URL=postgresql://opsdesk_prod:STRONG_PASSWORD@db-primary.internal:5432/opsdesk

# Security
JWT_SECRET=your-minimum-32-character-random-secret-string
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=7

# Environment
ENVIRONMENT=production
LOG_LEVEL=info

# Prometheus
PROMETHEUS_URL=https://prometheus.internal:9090

# Storage
ARTIFACT_STORAGE_PATH=/mnt/artifacts
MAX_ARTIFACT_SIZE_MB=500

# Frontend
NEXT_PUBLIC_API_URL=https://api.opsdesk.example.com

# CORS
CORS_ORIGINS=["https://opsdesk.example.com", "https://app.opsdesk.example.com"]

# Admin Seed
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=GENERATE_SECURE_PASSWORD
```

**Security Note**: Use secrets management system (AWS Secrets Manager, Vault) instead of .env in production.

## Docker Deployment

### Option 1: Docker Compose (Small Deployments)

```bash
# On production server
git clone https://github.com/gusdcoder/OpsDesk.git
cd OpsDesk

# Copy production env
cp env.example .env
# Edit .env with production values

# Build images
docker compose build

# Start services with restart policy
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Initialize database
docker exec opsdesk-api alembic upgrade head
docker exec opsdesk-api python -m app.seed_admin

# Enable auto-restart
docker update --restart always opsdesk-api
docker update --restart always opsdesk-ui
docker update --restart always opsdesk-db
```

**docker-compose.prod.yml**:
```yaml
version: '3.9'

services:
  postgres:
    restart: always
    networks:
      - opsdesk-net
    
  backend:
    restart: always
    environment:
      ENVIRONMENT: production
      LOG_LEVEL: info
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/readyz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - opsdesk-net
  
  frontend:
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - opsdesk-net

networks:
  opsdesk-net:
    driver: bridge
```

### Option 2: Kubernetes Deployment

**Example: OpsDesk Helm Chart structure**

```yaml
# helm/opsdesk/values-prod.yaml
replicas:
  backend: 3
  frontend: 2

image:
  repository: your-registry/opsdesk
  tag: v1.0.0
  pullPolicy: IfNotPresent

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: opsdesk.example.com
      paths:
        - path: /
          pathType: Prefix
          backend: frontend
        - path: /api
          pathType: Prefix
          backend: backend
  tls:
    - secretName: opsdesk-tls
      hosts:
        - opsdesk.example.com

postgresql:
  enabled: true
  auth:
    username: opsdesk
    password: STRONG_PASSWORD
  primary:
    persistence:
      size: 100Gi

resources:
  backend:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  frontend:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

## Nginx Reverse Proxy Configuration

```nginx
# /etc/nginx/sites-available/opsdesk.conf

upstream opsdesk_backend {
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
    keepalive 32;
}

upstream opsdesk_frontend {
    server frontend-1:3000;
    server frontend-2:3000;
    keepalive 32;
}

server {
    listen 80;
    server_name opsdesk.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name opsdesk.example.com;
    
    ssl_certificate /etc/letsencrypt/live/opsdesk.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/opsdesk.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;
    
    # API endpoints
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://opsdesk_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Auth endpoints (stricter rate limiting)
    location /api/auth/ {
        limit_req zone=auth_limit burst=5 nodelay;
        
        proxy_pass http://opsdesk_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend
    location / {
        proxy_pass http://opsdesk_frontend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health checks
    location /healthz {
        access_log off;
        proxy_pass http://opsdesk_backend;
    }
}
```

## Database Backup Strategy

### Automated Backup Script

```bash
#!/bin/bash
# /opt/opsdesk/backup.sh

BACKUP_DIR="/backups/opsdesk"
DB_NAME="opsdesk"
DB_USER="opsdesk_prod"
DB_HOST="db-primary.internal"
RETENTION_DAYS=30

# Daily backup
datestamp=$(date +"%Y%m%d_%H%M%S")
backup_file="$BACKUP_DIR/opsdesk_backup_$datestamp.sql.gz"

mkdir -p $BACKUP_DIR

PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | \
    gzip > $backup_file

# Upload to S3
aws s3 cp $backup_file s3://opsdesk-backups/

# Cleanup old backups
find $BACKUP_DIR -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $backup_file"
```

### Cron Schedule

```bash
# Run daily at 2 AM
0 2 * * * /opt/opsdesk/backup.sh >> /var/log/opsdesk-backup.log 2>&1

# Weekly full backup + upload
0 3 * * 0 /opt/opsdesk/backup-full.sh >> /var/log/opsdesk-backup-full.log 2>&1
```

## Monitoring & Observability

### Prometheus Scrape Config

```yaml
# /etc/prometheus/opsdesk.yml
scrape_configs:
  - job_name: 'opsdesk-api'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['opsdesk-api-1:8000', 'opsdesk-api-2:8000', 'opsdesk-api-3:8000']
  
  - job_name: 'opsdesk-db'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

### Alert Rules

```yaml
# /etc/prometheus/opsdesk-alerts.yml
groups:
  - name: opsdesk
    rules:
      - alert: OpsDesk API Down
        expr: up{job="opsdesk-api"} == 0
        for: 2m
        annotations:
          summary: "OpsDesk API is down"
      
      - alert: Database Connection Error
        expr: rate(opsdesk_db_connection_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High database connection errors"
      
      - alert: High Artifact Upload Rate
        expr: rate(opsdesk_artifact_uploads_total[5m]) > 100
        for: 10m
        annotations:
          summary: "Unusually high artifact upload rate"
```

## Scaling Strategies

### Horizontal Scaling

1. **Backend (Stateless)**
   - Add more FastAPI instances behind load balancer
   - Use connection pooling for database
   - Scale independently

2. **Frontend (Stateless)**
   - Add more Next.js instances
   - Use CDN for static assets
   - No coordination needed

3. **Database (Stateful)**
   - PostgreSQL replication (primary/replica)
   - Read replicas for analytics
   - Consider managed database services

### Vertical Scaling

- Increase instance CPU/memory if bottleneck identified
- Optimize queries if database is bottleneck
- Implement caching for frequently accessed data

## Disaster Recovery

### RTO/RPO Targets

- **RTO (Recovery Time Objective)**: 1 hour
- **RPO (Recovery Point Objective)**: 15 minutes

### Recovery Procedure

```bash
# 1. Restore database from backup
aws s3 cp s3://opsdesk-backups/latest-backup.sql.gz /tmp/
gunzip /tmp/latest-backup.sql.gz

# 2. Create new database
creatdb opsdesk_restore

# 3. Restore data
psql opsdesk_restore < /tmp/latest-backup.sql

# 4. Update connection string in config
# Point to restored database

# 5. Restart API servers
# Verify connectivity to new database

# 6. Test with synthetic requests
curl https://opsdesk.example.com/healthz
```

## Performance Tuning

### PostgreSQL

```sql
-- Enable connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET work_mem = '20MB';

-- Index optimization
CREATE INDEX idx_audit_events_actor_id_created_at ON audit_events(actor_user_id, created_at DESC);
CREATE INDEX idx_hosts_environment_criticality ON hosts(environment, criticality);
```

### FastAPI

```python
# app/config.py
db_pool_size = 20  # Connection pool size
db_max_overflow = 10  # Additional connections
request_timeout = 30  # Seconds
```

## Security Hardening

### Database Security

```sql
-- Create read-only user for backups
CREATE USER opsdesk_readonly WITH PASSWORD 'STRONG_PASSWORD';
GRANT CONNECT ON DATABASE opsdesk TO opsdesk_readonly;
GRANT USAGE ON SCHEMA public TO opsdesk_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO opsdesk_readonly;

-- Restrict network access
-- In pg_hba.conf:
# Only allow from internal subnet
host    opsdesk     opsdesk_prod    10.0.0.0/8    scram-sha-256
```

### API Security

```python
# CORS configuration
CORS_ORIGINS = [
    "https://opsdesk.example.com",
    "https://api.opsdesk.example.com"
]

# CSRF protection
CSRF_TRUSTED_ORIGINS = [
    "https://opsdesk.example.com"
]

# Rate limiting per endpoint
auth_limiter = RateLimiter(calls=5, period=60)  # 5 per minute
api_limiter = RateLimiter(calls=100, period=60)  # 100 per minute
```

## Troubleshooting Production Issues

### High Memory Usage

```bash
# Check memory leaks
docker stats opsdesk-api

# Restart if necessary
docker restart opsdesk-api
```

### Database Slow Queries

```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1 second
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
```

### Certificate Expiration

```bash
# Check certificate expiration
openssl s_client -connect opsdesk.example.com:443 -showcerts | grep "Not After"

# Renew with certbot
certbot renew --force-renewal

# Reload nginx
nginx -s reload
```
