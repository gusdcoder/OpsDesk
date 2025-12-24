from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import structlog
import logging
import sys

from app.config import settings
from app.models import Base
from app.routers import auth, hosts, artifacts, audit, users, settings as settings_router
from app.middleware.auth import AuthMiddleware
from app.middleware.audit import AuditMiddleware

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

handler = logging.StreamHandler(sys.stdout)
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="OpsDesk API",
    description="Enterprise Host Management & Telemetry Suite",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.add_middleware(AuditMiddleware)
app.add_middleware(AuthMiddleware)

# Database setup
engine = create_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(hosts.router, prefix="/hosts", tags=["hosts"])
app.include_router(artifacts.router, prefix="/artifacts", tags=["artifacts"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(settings_router.router, prefix="/settings", tags=["settings"])

# Dependency injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health checks
@app.get("/healthz")
async def health_check():
    """Liveness probe"""
    return {"status": "alive"}

@app.get("/readyz")
async def ready_check():
    """Readiness probe"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {
            "status": "ready",
            "database": "connected",
            "runtime_port": settings.runtime_port
        }
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)}
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "OpsDesk API",
        "version": "1.0.0",
        "runtime_port": settings.runtime_port,
        "docs": "/docs",
        "environment": settings.environment
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("starting_opsdesk_api", port=8000, environment=settings.environment, runtime_port=settings.runtime_port)
    uvicorn.run(app, host="0.0.0.0", port=8000)
