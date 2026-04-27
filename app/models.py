from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def now_utc():
    return datetime.now(timezone.utc)

class AuthUser(Base):
    __tablename__ = "auth_user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    password: Mapped[str] = mapped_column(String(128), default="")
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(150), default="")
    last_name: Mapped[str] = mapped_column(String(150), default="")
    email: Mapped[str] = mapped_column(String(254), index=True, default="")
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    date_joined: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    tokens: Mapped[list["AuthToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reported_incidents: Mapped[list["Incident"]] = relationship(back_populates="reported_by_user")

class AuthToken(Base):
    __tablename__ = "authtoken_token"
    key: Mapped[str] = mapped_column(String(40), primary_key=True, index=True)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    user_id: Mapped[int] = mapped_column(ForeignKey("auth_user.id"), unique=True, index=True)
    user: Mapped[AuthUser] = relationship(back_populates="tokens")

class UserProfile(Base):
    __tablename__ = "api_userprofile"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("auth_user.id"), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(20), default="bfp")
    avatar: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    user: Mapped[AuthUser] = relationship(back_populates="profile")

class Camera(Base):
    __tablename__ = "api_camera"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    camera_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(20), default="online")
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    footage_url: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    incidents: Mapped[list["Incident"]] = relationship(back_populates="camera_obj")

class Incident(Base):
    __tablename__ = "api_incident"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    incident_type: Mapped[str] = mapped_column(String(20))
    location: Mapped[str] = mapped_column(String(180))
    detection_method: Mapped[str] = mapped_column(String(20))
    time_reported: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    status: Mapped[str] = mapped_column(String(20), default="investigating")
    camera: Mapped[int | None] = mapped_column(ForeignKey("api_camera.id"), nullable=True)
    reported_by: Mapped[int | None] = mapped_column(ForeignKey("auth_user.id"), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    camera_obj: Mapped[Camera | None] = relationship(back_populates="incidents")
    reported_by_user: Mapped[AuthUser | None] = relationship(back_populates="reported_incidents")
