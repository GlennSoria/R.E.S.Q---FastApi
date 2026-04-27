from app.database import SessionLocal, Base, engine
from app.models import AuthUser, UserProfile, Camera, Incident
from app.security import django_pbkdf2_sha256
from datetime import datetime, timezone

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    def user(username,email,password,role):
        u = db.query(AuthUser).filter(AuthUser.username==username).first()
        if not u:
            u=AuthUser(username=username,email=email,password=django_pbkdf2_sha256(password)); db.add(u); db.commit(); db.refresh(u)
        else:
            u.email=email; u.password=django_pbkdf2_sha256(password); db.commit()
        if not u.profile:
            db.add(UserProfile(user_id=u.id, role=role)); db.commit()
        return u
    admin=user('admin','admin@gmail.com','admin123','admin')
    bfp=user('bfp','bfp@gmail.com','bfp123','bfp')
    def cam(code,name,location,status):
        c=db.query(Camera).filter(Camera.camera_code==code).first()
        if not c:
            c=Camera(camera_code=code,name=name,location=location,status=status); db.add(c); db.commit(); db.refresh(c)
        return c
    cam1=cam('CAM-001','Entrance Gate','Main Building','online')
    cam2=cam('CAM-002','Parking Lot A','North Wing','offline')
    cam('CAM-003','Lobby Camera','Reception','online')
    if not db.query(Incident).filter(Incident.incident_code=='INC-001').first():
        db.add(Incident(incident_code='INC-001',incident_type='fire',location='Zone A - North',detection_method='heat_sensor',status='resolved',camera=cam1.id,reported_by=admin.id,notes='Fire detected and resolved by response team.'))
    if not db.query(Incident).filter(Incident.incident_code=='INC-002').first():
        db.add(Incident(incident_code='INC-002',incident_type='gas',location='Zone C - Lobby',detection_method='camera_ai',status='investigating',camera=cam2.id,reported_by=bfp.id,notes='Gas trace under validation.'))
    db.commit(); print('Demo data seeded. admin/admin123, bfp/bfp123')
finally:
    db.close()
