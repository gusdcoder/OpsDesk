from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, JSON,
    ForeignKey, Table, Enum, LargeBinary, Float, BigInteger
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

# Association table for many-to-many tags
host_tags = Table(
    'host_tags',
    Base.metadata,
    Column('host_id', Integer, ForeignKey('hosts.id', ondelete='CASCADE')),
    Column('tag', String(50))
)

class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    VIEWER = "viewer"

class OSEnum(str, enum.Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"

class EnvironmentEnum(str, enum.Enum):
    PROD = "prod"
    STAGE = "stage"
    DEV = "dev"

class CriticalityEnum(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ConnectionMethodEnum(str, enum.Enum):
    DIRECT_SSH = "direct_ssh"
    BASTION_SSH = "bastion_ssh"
    TELEPORT = "teleport"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.VIEWER, nullable=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(32), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    audit_events = relationship('AuditEvent', back_populates='actor', foreign_keys='AuditEvent.actor_user_id')
    metrics = relationship('MetricsSnapshot', back_populates='collected_by_user')
    artifacts = relationship('Artifact', back_populates='uploaded_by_user')

class Host(Base):
    __tablename__ = 'hosts'
    
    id = Column(Integer, primary_key=True)
    hostname = Column(String(255), nullable=False, index=True)
    fqdn = Column(String(255), nullable=True)
    ip = Column(String(45), nullable=False, index=True)  # IPv4 or IPv6
    os = Column(Enum(OSEnum), nullable=False)
    environment = Column(Enum(EnvironmentEnum), default=EnvironmentEnum.DEV)
    owner = Column(String(255), nullable=True)
    team = Column(String(255), nullable=True)
    criticality = Column(Enum(CriticalityEnum), default=CriticalityEnum.LOW)
    tags = relationship('HostTag', secondary=host_tags, backref='hosts', cascade='all, delete')
    notes = Column(Text, nullable=True)
    connection_method = Column(Enum(ConnectionMethodEnum), default=ConnectionMethodEnum.DIRECT_SSH)
    smb_template = Column(Text, nullable=True)  # Template for SMB connector download
    ssh_template = Column(Text, nullable=True)  # Template for SSH command (e.g., ssh {{user}}@{{host}})
    bastion_host = Column(String(255), nullable=True)  # Optional bastion/jump host
    bastion_port = Column(Integer, default=22)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_seen = Column(DateTime, nullable=True)
    
    metrics_snapshots = relationship('MetricsSnapshot', back_populates='host', cascade='all, delete-orphan')
    artifacts = relationship('Artifact', back_populates='host', cascade='all, delete-orphan')

class HostTag(Base):
    __tablename__ = 'host_tags'
    
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete='CASCADE'), primary_key=True)
    tag = Column(String(50), primary_key=True)

class MetricsSnapshot(Base):
    __tablename__ = 'metrics_snapshots'
    
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete='CASCADE'), nullable=False, index=True)
    collected_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    collected_at = Column(DateTime, server_default=func.now())
    data = Column(JSON, nullable=False)  # {"cpu": {...}, "memory": {...}, "disk": {...}, "network": {...}}
    source = Column(String(50), default="prometheus")  # "prometheus" or "agent"
    ttl_expires_at = Column(DateTime, nullable=True, index=True)  # For cleanup
    
    host = relationship('Host', back_populates='metrics_snapshots')
    collected_by_user = relationship('User', back_populates='metrics')

class Artifact(Base):
    __tablename__ = 'artifacts'
    
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete='CASCADE'), nullable=False, index=True)
    uploaded_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # e.g., "log", "config", "binary", "credential"
    size_bytes = Column(BigInteger, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
    file_path = Column(String(512), nullable=False)  # Stored relative path
    description = Column(Text, nullable=True)
    
    host = relationship('Host', back_populates='artifacts')
    uploaded_by_user = relationship('User', back_populates='artifacts')

class AuditEvent(Base):
    __tablename__ = 'audit_events'
    
    id = Column(Integer, primary_key=True)
    actor_user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., "LOGIN", "HOST_CREATED", "ARTIFACT_UPLOADED"
    entity_type = Column(String(50), nullable=False)  # e.g., "USER", "HOST", "ARTIFACT"
    entity_id = Column(String(50), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional context
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    actor = relationship('User', back_populates='audit_events', foreign_keys=[actor_user_id])

class Setting(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
