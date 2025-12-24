import os
import uuid
from pathlib import Path
from typing import BinaryIO, Optional
from app.config import settings
import structlog

logger = structlog.get_logger()

class FileHandler:
    def __init__(self, storage_path: str = None):
        self.storage_path = Path(storage_path or settings.artifact_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_artifact(self, file_obj: BinaryIO, original_filename: str, host_id: int) -> tuple[str, int]:
        """Save uploaded file and return (relative_path, size_bytes)"""
        try:
            # Create host-specific directory
            host_dir = self.storage_path / f"host_{host_id}"
            host_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            file_ext = Path(original_filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = host_dir / unique_filename
            
            # Write file
            file_size = 0
            with open(file_path, 'wb') as f:
                while chunk := file_obj.read(8192):
                    f.write(chunk)
                    file_size += len(chunk)
            
            # Check size limit
            max_size = settings.max_artifact_size_mb * 1024 * 1024
            if file_size > max_size:
                file_path.unlink()
                raise ValueError(f"File exceeds maximum size of {settings.max_artifact_size_mb}MB")
            
            relative_path = f"host_{host_id}/{unique_filename}"
            logger.info("artifact_saved", path=relative_path, size=file_size)
            return relative_path, file_size
        except Exception as e:
            logger.error("file_save_error", filename=original_filename, error=str(e))
            raise
    
    def get_artifact_path(self, relative_path: str) -> Optional[Path]:
        """Get full path to artifact"""
        full_path = self.storage_path / relative_path
        if full_path.exists() and full_path.is_file():
            return full_path
        return None
    
    def delete_artifact(self, relative_path: str) -> bool:
        """Delete artifact file"""
        try:
            full_path = self.storage_path / relative_path
            if full_path.exists():
                full_path.unlink()
                logger.info("artifact_deleted", path=relative_path)
                return True
            return False
        except Exception as e:
            logger.error("file_delete_error", path=relative_path, error=str(e))
            return False

file_handler = FileHandler()
