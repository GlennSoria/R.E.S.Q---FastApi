from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..deps import get_current_user
from ..models import Incident, Camera, AuthUser
from ..schemas import IncidentCreate, IncidentUpdate, IncidentOut

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

def out(i: Incident) -> IncidentOut:
    return IncidentOut(
        id=i.id, incident_code=i.incident_code, incident_type=i.incident_type, location=i.location,
        detection_method=i.detection_method, time_reported=i.time_reported, status=i.status,
        camera=i.camera, camera_code=i.camera_obj.camera_code if i.camera_obj else None,
        reported_by=i.reported_by, reported_by_username=i.reported_by_user.username if i.reported_by_user else None,
        notes=i.notes or "", created_at=i.created_at, updated_at=i.updated_at,
    )

@router.get("/", response_model=list[IncidentOut])
def list_incidents(user: AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(Incident).options(joinedload(Incident.camera_obj), joinedload(Incident.reported_by_user)).order_by(Incident.time_reported.desc()).all()
    return [out(i) for i in items]

@router.post("/", response_model=IncidentOut, status_code=201)
def create_incident(data: IncidentCreate, user: AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(Incident).filter(Incident.incident_code == data.incident_code).first():
        raise HTTPException(400, "Incident code already exists.")
    vals = data.model_dump()
    if vals.get("time_reported") is None: vals["time_reported"] = datetime.now(timezone.utc)
    if vals.get("camera") is not None and not db.get(Camera, vals["camera"]):
        raise HTTPException(400, "Camera does not exist.")
    obj = Incident(**vals, reported_by=user.id)
    db.add(obj); db.commit(); db.refresh(obj)
    obj = db.query(Incident).options(joinedload(Incident.camera_obj), joinedload(Incident.reported_by_user)).get(obj.id)
    return out(obj)

@router.get("/{incident_id}/", response_model=IncidentOut)
def get_incident(incident_id: int, user: AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    obj = db.query(Incident).options(joinedload(Incident.camera_obj), joinedload(Incident.reported_by_user)).get(incident_id)
    if not obj: raise HTTPException(404, "Not found.")
    return out(obj)

@router.put("/{incident_id}/", response_model=IncidentOut)
def update_incident(incident_id: int, data: IncidentUpdate, user: AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    obj = db.get(Incident, incident_id)
    if not obj: raise HTTPException(404, "Not found.")
    vals = data.model_dump()
    if vals.get("time_reported") is None: vals["time_reported"] = datetime.now(timezone.utc)
    if vals.get("camera") is not None and not db.get(Camera, vals["camera"]): raise HTTPException(400, "Camera does not exist.")
    dupe = db.query(Incident).filter(Incident.incident_code == vals["incident_code"], Incident.id != incident_id).first()
    if dupe: raise HTTPException(400, "Incident code already exists.")
    for k,v in vals.items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj)
    obj = db.query(Incident).options(joinedload(Incident.camera_obj), joinedload(Incident.reported_by_user)).get(obj.id)
    return out(obj)

@router.delete("/{incident_id}/", status_code=204)
def delete_incident(incident_id: int, user: AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    obj = db.get(Incident, incident_id)
    if not obj: raise HTTPException(404, "Not found.")
    db.delete(obj); db.commit(); return Response(status_code=204)
