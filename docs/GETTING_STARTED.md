# Getting Started with OpsDesk

## Prerequisites

- Docker & Docker Compose (for containerized setup)
- OR:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 16

## Quick Start (Docker Compose)

The fastest way to get OpsDesk running:

```bash
# 1. Clone repository
git clone https://github.com/gusdcoder/OpsDesk.git
cd OpsDesk

# 2. Configure environment
cp env.example .env
# Edit .env if needed (defaults work for local development)

# 3. Start all services
docker compose up --build

# Wait for services to start (~30 seconds)
# You'll see "Application startup complete" in the backend logs

# 4. Initialize database (in another terminal)
docker exec opsdesk-api alembic upgrade head
docker exec opsdesk-api python -m app.seed_admin

# 5. Access services
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432
```

### Default Login

```
Email:    admin@opsdesk.local
Password: SecurePassword123 (or value of ADMIN_PASSWORD env var)
```

## Local Development (Without Docker)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to point to local PostgreSQL

# Run migrations
alembic upgrade head

# Seed admin user
python -m app.seed_admin

# Start API server
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
# Navigate to frontend (in another terminal)
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Frontend will be available at http://localhost:3000
```

## Verifying Installation

### Health Checks

```bash
# Liveness check
curl http://localhost:8000/healthz
# Response: {"status":"alive"}

# Readiness check
curl http://localhost:8000/readyz
# Response: {"status":"ready","database":"connected","runtime_port":XXXXX}
```

### API Documentation

Interactive API documentation available at:
```
http://localhost:8000/docs
```

Alternative ReDoc documentation:
```
http://localhost:8000/redoc
```

## First Steps

### 1. Create Your First Host

```bash
curl -X POST http://localhost:8000/hosts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "web-server-01",
    "ip": "10.0.1.10",
    "os": "linux",
    "environment": "prod",
    "criticality": "high",
    "owner": "devops-team"
  }'
```

### 2. Import Multiple Hosts from CSV

**CSV Format** (hosts.csv):
```
hostname,ip,fqdn,os,environment,owner,team,criticality,notes
web-01,10.0.1.10,web-01.prod.com,linux,prod,ops,platform,high,Primary Web Server
db-01,10.0.2.10,db-01.prod.com,linux,prod,dba,platform,critical,Master Database
dev-01,10.0.3.10,dev-01.dev.com,linux,dev,devops,platform,low,Development Server
```

**Upload:**
```bash
curl -X POST http://localhost:8000/hosts/import-csv \
  -H "Authorization: Bearer <token>" \
  -F "file=@hosts.csv"
```

### 3. Get SSH Command for a Host

```bash
# Get host details (includes ssh_template)
curl http://localhost:8000/hosts/1 \
  -H "Authorization: Bearer <token>"

# Example response includes ssh_template like:
# "ssh_template": "ssh {{user}}@{{host}} -p {{port}} -J {{bastion}}"

# Substitute variables manually or use in your automation
```

### 4. Collect Metrics

```bash
# Requires Prometheus configured at PROMETHEUS_URL
curl -X POST http://localhost:8000/hosts/1/metrics:update \
  -H "Authorization: Bearer <token>"

# Response includes metrics like CPU, memory, disk, uptime
```

### 5. Upload an Artifact

```bash
curl -X POST http://localhost:8000/artifacts/1/artifacts \
  -H "Authorization: Bearer <token>" \
  -F "file=@app.log" \
  -F "file_type=log"
```

## Environment Configuration

### Required Variables

| Variable | Purpose | Example |
|----------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@localhost/opsdesk` |
| `JWT_SECRET` | Token signing | `your-random-secret-min-32-chars` |
| `ADMIN_EMAIL` | Initial admin email | `admin@opsdesk.local` |
| `ADMIN_PASSWORD` | Initial admin password | `SecurePassword123` |

### Optional Variables

| Variable | Default | Purpose |
|----------|---------|----------|
| `ENVIRONMENT` | `development` | Deployment environment |
| `PROMETHEUS_URL` | `http://prometheus:9090` | Metrics source |
| `JWT_EXPIRATION_HOURS` | `24` | Token lifetime |
| `ARTIFACT_STORAGE_PATH` | `/artifacts` | File storage location |
| `MAX_ARTIFACT_SIZE_MB` | `100` | Upload size limit |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed domains |

## Stopping Services

```bash
# Stop all services (keeps data)
docker compose down

# Stop and remove volumes (deletes data)
docker compose down -v

# Stop specific service
docker compose stop backend
```

## Troubleshooting

### Database Connection Failed

```bash
# Check if PostgreSQL is running
docker exec opsdesk-db pg_isready

# View database logs
docker compose logs postgres

# Reset database
docker compose down -v
docker compose up
```

### Migration Errors

```bash
# Reset migrations
docker exec opsdesk-api alembic downgrade base
docker exec opsdesk-api alembic upgrade head
```

### API not responding

```bash
# Check API logs
docker compose logs backend

# Restart API
docker compose restart backend
```

### Frontend not loading

```bash
# Check frontend logs
docker compose logs frontend

# Clear Next.js cache
docker compose exec frontend rm -rf .next
docker compose restart frontend
```

## Next Steps

1. **Read Architecture** - Understand system design: [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Review Security** - Learn threat model: [THREAT_MODEL.md](THREAT_MODEL.md)
3. **Explore API** - Full endpoint reference: [API.md](API.md)
4. **Database Design** - See ERD: [ERD.md](ERD.md)
5. **Deploy to Production** - Follow deployment guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## Support & Resources

- **Documentation**: All docs are in `/docs` directory
- **Issue Tracking**: GitHub Issues for bug reports
- **API Help**: Interactive docs at `/docs` endpoint
