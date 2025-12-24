from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class RoleEnum(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    VIEWER = "viewer"

class OSEnum(str, Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"

class EnvironmentEnum(str, Enum):
    PROD = "prod"
    STAGE = "stage"
    DEV = "dev"

class CriticalityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ConnectionMethodEnum(str, Enum):
    DIRECT_SSH = "direct_ssh"
    BASTION_SSH = "bastion_ssh"
    TELEPORT = "teleport"

# Auth
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str

# Users
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: RoleEnum = RoleEnum.VIEWER
    
    @field_validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None

class UserResponse(BaseModel):
    id: int
    email: str
    role: RoleEnum
    mfa_enabled: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Hosts
class HostCreate(BaseModel):
    hostname: str
    fqdn: Optional[str] = None
    ip: str
    os: OSEnum
    environment: EnvironmentEnum = EnvironmentEnum.DEV
    owner: Optional[str] = None
    team: Optional[str] = None
    criticality: CriticalityEnum = CriticalityEnum.LOW
    tags: List[str] = []
    notes: Optional[str] = None
    connection_method: ConnectionMethodEnum = ConnectionMethodEnum.DIRECT_SSH
    smb_template: Optional[str] = None
    ssh_template: Optional[str] = None
    bastion_host: Optional[str] = None
    bastion_port: int = 22

class HostUpdate(BaseModel):
    hostname: Optional[str] = None
    fqdn: Optional[str] = None
    ip: Optional[str] = None
    environment: Optional[EnvironmentEnum] = None
    owner: Optional[str] = None
    team: Optional[str] = None
    criticality: Optional[CriticalityEnum] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    connection_method: Optional[ConnectionMethodEnum] = None
    smb_template: Optional[str] = None
    ssh_template: Optional[str] = None
    bastion_host: Optional[str] = None
    bastion_port: Optional[int] = None

class HostResponse(BaseModel):
    id: int
    hostname: str
    fqdn: Optional[str]
    ip: str
    os: OSEnum
    environment: EnvironmentEnum
    owner: Optional[str]
    team: Optional[str]
    criticality: CriticalityEnum
    tags: List[str]
    notes: Optional[str]
    connection_method: ConnectionMethodEnum
    smb_template: Optional[str]
    ssh_template: Optional[str]
    bastion_host: Optional[str]
    bastion_port: int
    created_at: datetime
    updated_at: datetime
    last_seen: Optional[datetime]
    
    class Config:
        from_attributes = True

# Metrics
class MetricsData(BaseModel):
    cpu: Optional[Dict[str, Any]] = None
    memory: Optional[Dict[str, Any]] = None
    disk: Optional[Dict[str, Any]] = None
    network: Optional[Dict[str, Any]] = None
    uptime: Optional[str] = None
    processes: Optional[List[Dict[str, Any]]] = None

class MetricsSnapshot(BaseModel):
    id: int
    host_id: int
    data: MetricsData
    collected_at: datetime
    collected_by_user_id: int
    source: str
    
    class Config:
        from_attributes = True

# Artifacts
class ArtifactCreate(BaseModel):
    name: str
    file_type: str
    description: Optional[str] = None

class ArtifactResponse(BaseModel):
    id: int
    host_id: int
    name: str
    file_type: str
    size_bytes: int
    uploaded_at: datetime
    uploaded_by_user_id: int
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

# Audit
class AuditEventResponse(BaseModel):
    id: int
    actor_user_id: Optional[int]
    action: str
    entity_type: str
    entity_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Settings
class SettingsResponse(BaseModel):
    prometheus_url: str
    runtime_port: int
    max_artifact_size_mb: int

class IntegrationsSettings(BaseModel):
    prometheus_url: str
    ssh_template: Optional[str] = None
    smb_template: Optional[str] = None
