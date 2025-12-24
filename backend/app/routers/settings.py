from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.schemas import SettingsResponse, IntegrationsSettings
from app.main import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/runtime")
async def get_runtime_settings():
    """Get runtime configuration including dynamically assigned port"""
    return {
        "runtime_port": settings.runtime_port,
        "environment": settings.environment,
        "prometheus_url": settings.prometheus_url,
        "max_artifact_size_mb": settings.max_artifact_size_mb
    }

@router.get("/integrations")
async def get_integrations():
    """Get integration settings"""
    return {
        "prometheus_url": settings.prometheus_url,
        "artifact_storage_path": settings.artifact_storage_path
    }

@router.put("/integrations")
async def update_integrations(config: IntegrationsSettings):
    """Update integration settings"""
    # In production, would persist to database
    return {"message": "Settings updated", "config": config}
