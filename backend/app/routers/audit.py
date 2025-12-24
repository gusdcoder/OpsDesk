from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models import AuditEvent
from app.schemas import AuditEventResponse
from app.main import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[AuditEventResponse])
async def list_audit_events(
    skip: int = Query(0),
    limit: int = Query(100),
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List audit events with filters"""
    query = db.query(AuditEvent)
    
    if action:
        query = query.filter(AuditEvent.action == action)
    if entity_type:
        query = query.filter(AuditEvent.entity_type == entity_type)
    
    events = query.order_by(AuditEvent.created_at.desc()).offset(skip).limit(limit).all()
    return events

@router.get("/export/csv")
async def export_audit_logs(db: Session = Depends(get_db)):
    """Export audit logs as CSV"""
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    events = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Actor', 'Action', 'Entity Type', 'Entity ID', 'IP Address', 'Timestamp'])
    
    for event in events:
        writer.writerow([
            event.id,
            event.actor_user_id,
            event.action,
            event.entity_type,
            event.entity_id,
            event.ip_address,
            event.created_at
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
    )
