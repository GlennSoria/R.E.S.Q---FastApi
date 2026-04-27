from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict

Role = Literal["admin", "bfp"]
CameraStatus = Literal["online", "offline", "maintenance"]
IncidentType = Literal["fire", "gas", "smoke", "other"]
DetectionMethod = Literal["heat_sensor", "camera_ai", "gas_sensor", "manual"]
IncidentStatus = Literal["open", "investigating", "resolved"]

class UserProfileOut(BaseModel):
    username: str
    email: str
    role: str = "bfp"
    avatar: str = ""

class RegisterIn(BaseModel):
    username: str | None = ""
    email: EmailStr
    password: str = Field(min_length=6)
    role: Role = "bfp"
    avatar: str = ""

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    message: str
    token: str
    user: UserProfileOut

class CameraBase(BaseModel):
    camera_code: str = Field(max_length=20)
    name: str = Field(max_length=120)
    location: str = Field(max_length=160)
    status: CameraStatus = "online"
    last_active: datetime | None = None
    footage_url: str = ""

class CameraCreate(CameraBase): pass
class CameraUpdate(CameraBase): pass

class CameraOut(CameraBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IncidentBase(BaseModel):
    incident_code: str = Field(max_length=20)
    incident_type: IncidentType
    location: str = Field(max_length=180)
    detection_method: DetectionMethod
    time_reported: datetime | None = None
    status: IncidentStatus = "investigating"
    camera: Optional[int] = None
    notes: str = ""

class IncidentCreate(IncidentBase): pass
class IncidentUpdate(IncidentBase): pass

class IncidentOut(IncidentBase):
    id: int
    reported_by: Optional[int] = None
    camera_code: Optional[str] = None
    reported_by_username: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SystemOverview(BaseModel):
    camera_count: int
    incident_count: int
    open_incidents: int
    resolved_incidents: int
