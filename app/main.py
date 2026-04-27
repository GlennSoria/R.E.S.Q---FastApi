from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine
from . import models
from .routers import auth, cameras, incidents, system

app = FastAPI(title="RESQ FastAPI - Option A Django Compatible")

origins = ["*"] if settings.cors_allow_origins == "*" else [o.strip() for o in settings.cors_allow_origins.split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "RESQ FastAPI Option A running", "docs": "/docs"}

app.include_router(auth.router)
app.include_router(cameras.router)
app.include_router(incidents.router)
app.include_router(system.router)
