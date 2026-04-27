from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import Camera, AuthUser
from ..schemas import CameraCreate, CameraUpdate, CameraOut

router = APIRouter(prefix="/api/cameras", tags=["Cameras"], dependencies=[Depends(get_current_user)])

def apply_camera(obj: Camera, data):
    values = data.model_dump()
    if values.get("last_active") is None:
        values["last_active"] = datetime.now(timezone.utc)
    for k,v in values.items(): setattr(obj,k,v)

@router.get("/", response_model=list[CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).order_by(Camera.camera_code).all()

@router.post("/", response_model=CameraOut, status_code=201)
def create_camera(data: CameraCreate, db: Session = Depends(get_db)):
    if db.query(Camera).filter(Camera.camera_code == data.camera_code).first():
        raise HTTPException(status_code=400, detail="Camera code already exists.")
    obj = Camera(**data.model_dump(exclude_none=True))
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/{camera_id}/", response_model=CameraOut)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    obj = db.get(Camera, camera_id)
    if not obj: raise HTTPException(404, "Not found.")
    return obj

@router.put("/{camera_id}/", response_model=CameraOut)
def update_camera(camera_id: int, data: CameraUpdate, db: Session = Depends(get_db)):
    obj = db.get(Camera, camera_id)
    if not obj: raise HTTPException(404, "Not found.")
    dupe = db.query(Camera).filter(Camera.camera_code == data.camera_code, Camera.id != camera_id).first()
    if dupe: raise HTTPException(400, "Camera code already exists.")
    apply_camera(obj, data); db.commit(); db.refresh(obj); return obj

@router.delete("/{camera_id}/", status_code=204)
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    obj = db.get(Camera, camera_id)
    if not obj: raise HTTPException(404, "Not found.")
    db.delete(obj); db.commit(); return Response(status_code=204)
