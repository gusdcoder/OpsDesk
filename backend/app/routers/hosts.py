from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
import structlog
from datetime import datetime

from app.schemas import HostCreate, HostUpdate, HostResponse, OSEnum, EnvironmentEnum, CriticalityEnum, ConnectionMethodEnum
from app.models import Host, User, AuditEvent, RoleEnum as ModelRoleEnum
from app.utils.prometheus_client import prometheus_client
from app.main import SessionLocal

router = APIRouter()
logger = structlog.get_logger()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=HostResponse)
async def create_host(host: HostCreate, db: Session = Depends(get_db)):
    """Create a new host"""
    existing = db.query(Host).filter(Host.ip == host.ip).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Host with this IP already exists")
    
    db_host = Host(
        hostname=host.hostname,
        fqdn=host.fqdn,
        ip=host.ip,
        os=host.os,
        environment=host.environment,
        owner=host.owner,
        team=host.team,
        criticality=host.criticality,
        notes=host.notes,
        connection_method=host.connection_method,
        smb_template=host.smb_template,
        ssh_template=host.ssh_template,
        bastion_host=host.bastion_host,
        bastion_port=host.bastion_port
    )
    
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    
    logger.info("host_created", host_id=db_host.id, hostname=db_host.hostname, ip=db_host.ip)
    
    return db_host

@router.get("/", response_model=List[HostResponse])
async def list_hosts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    environment: Optional[EnvironmentEnum] = None,
    os: Optional[OSEnum] = None,
    criticality: Optional[CriticalityEnum] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db) = None
):
    """List hosts with filters"""
    query = db.query(Host)
    
    if environment:
        query = query.filter(Host.environment == environment)
    if os:
        query = query.filter(Host.os == os)
    if criticality:
        query = query.filter(Host.criticality == criticality)
    
    hosts = query.offset(skip).limit(limit).all()
    return hosts

@router.get("/{host_id}", response_model=HostResponse)
async def get_host(host_id: int, db: Session = Depends(get_db)):
    """Get a specific host"""
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    return host

@router.put("/{host_id}", response_model=HostResponse)
async def update_host(host_id: int, host_update: HostUpdate, db: Session = Depends(get_db)):
    """Update a host"""
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    
    update_data = host_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(host, field, value)
    
    db.commit()
    db.refresh(host)
    
    logger.info("host_updated", host_id=host_id)
    return host

@router.delete("/{host_id}")
async def delete_host(host_id: int, db: Session = Depends(get_db)):
    """Delete a host"""
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    
    db.delete(host)
    db.commit()
    
    logger.info("host_deleted", host_id=host_id)
    return {"message": "Host deleted"}

@router.post("/import-csv")
async def import_hosts_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import hosts from CSV"""
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode('utf-8')))
    
    imported_count = 0
    for row in reader:
        try:
            host = Host(
                hostname=row['hostname'],
                fqdn=row.get('fqdn'),
                ip=row['ip'],
                os=row.get('os', 'linux'),
                environment=row.get('environment', 'dev'),
                owner=row.get('owner'),
                team=row.get('team'),
                criticality=row.get('criticality', 'low'),
                notes=row.get('notes')
            )
            db.add(host)
            imported_count += 1
        except Exception as e:
            logger.error("csv_import_error", row=row, error=str(e))
            continue
    
    db.commit()
    logger.info("hosts_imported_from_csv", count=imported_count)
    return {"imported": imported_count}

@router.post("/{host_id}/metrics:update")
async def update_metrics(host_id: int, db: Session = Depends(get_db)):
    """Trigger on-demand metrics collection from Prometheus"""
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    
    # Query Prometheus
    metrics = await prometheus_client.get_host_metrics(host.hostname)
    if not metrics:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to collect metrics")
    
    logger.info("metrics_collected", host_id=host_id, hostname=host.hostname)
    return {"host_id": host_id, "metrics": metrics, "collected_at": datetime.now().isoformat()}

@router.get("/{host_id}/metrics:latest")
async def get_latest_metrics(host_id: int, db: Session = Depends(get_db)):
    """Get latest metrics snapshot for a host"""
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    
    # Return latest snapshot if available
    latest = db.query(Host).filter(Host.id == host_id).first().metrics_snapshots
    if latest:
        return {"metrics": latest[0].data, "collected_at": latest[0].collected_at}
    
    return {"metrics": None, "message": "No metrics collected yet"}
