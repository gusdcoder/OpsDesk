# OpsDesk - Enterprise Host Management & Telemetry Suite

A professional, containerized system for managing remote hosts, orchestrating SSH connections, and collecting on-demand telemetry. Built for authorized IT/SecOps teams.

## 🎯 Features

- **Host Inventory Management**: CRUD operations for Windows/Linux/macOS hosts with tags, environments, and criticality levels
- **RBAC & Authentication**: Role-based access (Admin, Operator, Auditor, Viewer) with Argon2 hashing and MFA support
- **SSH Session Management**: Generate SSH commands via bastions (OpenSSH, Teleport) with session intent logging
- **On-Demand Telemetry**: Prometheus-based metrics (CPU, Memory, Disk, Network, Uptime) collected on-demand
- **Stageless Connectivity**: SMB template-based connector downloads for initial access
- **Artifact Management**: Upload, store, and manage data exfiltrated from hosts with full audit trails
- **Comprehensive Audit Logging**: Track all user actions with searchable, filterable logs
- **Enterprise UI**: Professional SaaS design with responsive layouts and Shadcn/UI components

## 📋 Tech Stack

### Frontend
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS + Shadcn/UI
- Lucide-React (icons)
- React Query (data fetching)

### Backend
- Python 3.11+
- FastAPI (async)
- SQLAlchemy 2.0 (ORM)
- Pydantic v2 (validation)
- Alembic (migrations)
- Prometheus client

### Infrastructure
- PostgreSQL 16
- Docker & Docker Compose
- JWT authentication

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (local development)
- Node.js 18+ (local frontend development)

### Setup

1. **Clone & Configure**
   ```bash
   git clone https://github.com/gusdcoder/OpsDesk.git
   cd OpsDesk
   cp env.example .env
   # Edit .env with your values
   ```

2. **Start Services**
   ```bash
   docker compose up --build
   ```

3. **Initialize Database**
   ```bash
   docker exec opsdesk-api alembic upgrade head
   docker exec opsdesk-api python -m app.seed_admin
   ```

4. **Access**
   - UI: http://localhost:3000
   - API: http://localhost:8000/docs
   - Default: admin@opsdesk.local / (from ADMIN_PASSWORD env)

## 📁 Project Structure

```
OpsDesk/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── hosts.py
│   │   │   ├── artifacts.py
│   │   │   ├── audit.py
│   │   │   ├── users.py
│   │   │   └── settings.py
│   │   ├── middleware/
│   │   │   ├── auth.py
│   │   │   └── audit.py
│   │   ├── utils/
│   │   │   ├── prometheus_client.py
│   │   │   ├── auth_utils.py
│   │   │   └── file_handler.py
│   │   ├── seed_admin.py        # Initial admin creation
│   │   └── config.py            # Settings & env
│   ├── alembic/
│   │   └── versions/            # DB migrations
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── login/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── hosts/
│   │   ├── artifacts/page.tsx
│   │   ├── audit/page.tsx
│   │   ├── settings/page.tsx
│   │   └── users/page.tsx
│   ├── components/
│   │   ├── layout/
│   │   ├── hosts/
│   │   ├── artifacts/
│   │   ├── auth/
│   │   └── common/
│   ├── hooks/
│   ├── lib/
│   │   └── api.ts              # API client
│   ├── Dockerfile
│   ├── package.json
│   └── next.config.js
├── infra/
│   └── docker-compose.yml
├── docs/
│   ├── README.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── THREAT_MODEL.md
│   └── ERD.md
└── docker-compose.yml
```

## 🔐 Security

- Passwords hashed with Argon2
- JWT tokens with configurable expiration
- RBAC enforced on all endpoints
- Append-only audit logs
- CSRF protection on state-changing endpoints
- Rate limiting on auth endpoints
- Secrets managed via environment variables

## 📖 Documentation

- [API Documentation](docs/API.md) - Endpoint reference
- [Architecture](docs/ARCHITECTURE.md) - System design & data flow
- [Threat Model](docs/THREAT_MODEL.md) - Security analysis
- [ERD](docs/ERD.md) - Entity relationship diagram

## 🧪 Testing

```bash
# Backend
cd backend
pip install -r requirements-dev.txt
pytest

# Frontend
cd frontend
npm install
npm test
```

## 📊 Environment Variables

See `env.example` for complete list. Key variables:

| Variable | Purpose | Default |
|----------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection | postgres://... |
| `JWT_SECRET` | Token signing secret | (required) |
| `PROMETHEUS_URL` | Metrics source | http://prometheus:9090 |
| `ARTIFACT_STORAGE_PATH` | File upload location | /artifacts |
| `ENVIRONMENT` | Deployment environment | development |

## 🛠️ Development Workflow

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Create feature branch (`git checkout -b feature/my-feature`)
2. Commit changes (`git commit -am 'Add feature'`)
3. Push to branch (`git push origin feature/my-feature`)
4. Open Pull Request

## 📧 Support

For issues, questions, or contributions, open an issue on GitHub.
