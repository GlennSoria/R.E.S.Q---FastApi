from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import Camera, Incident
from ..schemas import SystemOverview

router = APIRouter(prefix="/api/system", tags=["System"], dependencies=[Depends(get_current_user)])

@router.get("/overview/", response_model=SystemOverview)
def system_overview(db: Session = Depends(get_db)):
    return SystemOverview(
        camera_count=db.query(Camera).count(),
        incident_count=db.query(Incident).count(),
        open_incidents=db.query(Incident).filter(Incident.status.in_(["open", "investigating"])).count(),
        resolved_incidents=db.query(Incident).filter(Incident.status == "resolved").count(),
    )
