from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
import structlog

from app.models import Artifact, Host
from app.schemas import ArtifactResponse, ArtifactCreate
from app.utils.file_handler import file_handler
from app.main import SessionLocal

router = APIRouter()
logger = structlog.get_logger()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{host_id}/artifacts", response_model=ArtifactResponse)
async def upload_artifact(
    host_id: int,
    file: UploadFile = File(...),
    file_type: str = Query(...),
    db: Session = Depends(get_db)
):
    """Upload an artifact for a host"""
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    
    try:
        # Save file
        relative_path, file_size = await file_handler.save_artifact(
            file.file, file.filename, host_id
        )
        
        # Create artifact record
        artifact = Artifact(
            host_id=host_id,
            name=file.filename,
            file_type=file_type,
            size_bytes=file_size,
            file_path=relative_path,
            uploaded_by_user_id=1  # Would be from auth middleware
        )
        
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        
        logger.info("artifact_uploaded", artifact_id=artifact.id, host_id=host_id, size=file_size)
        return artifact
    except Exception as e:
        logger.error("artifact_upload_error", host_id=host_id, error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{host_id}/artifacts", response_model=List[ArtifactResponse])
async def list_artifacts(
    host_id: int,
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    """List artifacts for a host"""
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    
    artifacts = db.query(Artifact).filter(Artifact.host_id == host_id).offset(skip).limit(limit).all()
    return artifacts

@router.get("/artifacts/{artifact_id}/download")
async def download_artifact(artifact_id: int, db: Session = Depends(get_db)):
    """Download an artifact"""
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    
    file_path = file_handler.get_artifact_path(artifact.file_path)
    if not file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    logger.info("artifact_downloaded", artifact_id=artifact_id)
    
    from fastapi.responses import FileResponse
    return FileResponse(file_path, filename=artifact.name)

@router.delete("/artifacts/{artifact_id}")
async def delete_artifact(artifact_id: int, db: Session = Depends(get_db)):
    """Delete an artifact"""
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    
    file_handler.delete_artifact(artifact.file_path)
    db.delete(artifact)
    db.commit()
    
    logger.info("artifact_deleted", artifact_id=artifact_id)
    return {"message": "Artifact deleted"}
