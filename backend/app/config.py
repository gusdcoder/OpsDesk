from pydantic_settings import BaseSettings
from typing import List
import random
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://opsdesk_user:secure_dev_password@localhost:5432/opsdesk"
    
    # JWT
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 7
    
    # Environment
    environment: str = "development"
    log_level: str = "info"
    
    # Prometheus
    prometheus_url: str = "http://prometheus:9090"
    
    # Artifacts
    artifact_storage_path: str = "/artifacts"
    max_artifact_size_mb: int = 100
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Runtime Port (randomly assigned on startup)
    runtime_port: int = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate random port on startup if not set
        if not self.runtime_port:
            self.runtime_port = random.randint(41000, 45000)

settings = Settings()
