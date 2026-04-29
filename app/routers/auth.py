from fastapi import APIRouter, Depends, HTTPException
from fastapi import Header, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import AuthUser, UserProfile, AuthToken
from ..schemas import RegisterIn, LoginIn, AuthResponse, UserProfileOut
from ..security import django_pbkdf2_sha256, verify_django_password, make_token
from ..deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def profile_out(profile: UserProfile) -> UserProfileOut:
    return UserProfileOut(username=profile.user.username, email=profile.user.email, role=profile.role, avatar=profile.avatar or "")

def get_or_create_profile(db: Session, user: AuthUser) -> UserProfile:
    if user.profile:
        return user.profile
    profile = UserProfile(user_id=user.id)
    db.add(profile); db.commit(); db.refresh(profile)
    return profile

def create_new_token(db: Session, user: AuthUser) -> AuthToken:
    # Delete old token/s of this user
    db.query(AuthToken).filter(AuthToken.user_id == user.id).delete()
    db.commit()

    # Create fresh token
    token = AuthToken(key=make_token(), user_id=user.id)
    db.add(token)
    db.commit()
    db.refresh(token)

    return token

@router.post("/register/", response_model=AuthResponse, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if db.query(AuthUser).filter(func.lower(AuthUser.email) == email).first():
        raise HTTPException(status_code=400, detail={"email": ["Email is already registered."]})
    username = (data.username or "").strip()
    if not username:
        base = email.split("@")[0]
        username = base; counter = 1
        while db.query(AuthUser).filter(func.lower(AuthUser.username) == username.lower()).first():
            counter += 1; username = f"{base}{counter}"
    elif db.query(AuthUser).filter(func.lower(AuthUser.username) == username.lower()).first():
        raise HTTPException(status_code=400, detail={"username": ["Username is already registered."]})
    user = AuthUser(username=username, email=email, password=django_pbkdf2_sha256(data.password))
    db.add(user); db.commit(); db.refresh(user)
    profile = UserProfile(user_id=user.id, role=data.role, avatar=data.avatar or "")
    db.add(profile); db.commit(); db.refresh(profile)
    token = get_or_create_token(db, user)
    return AuthResponse(message="User registered successfully.", token=token.key, user=profile_out(profile))

@router.post("/login/", response_model=AuthResponse)
def login(data: LoginIn, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.query(AuthUser).filter(func.lower(AuthUser.email) == email).first()
    if not user or not verify_django_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    profile = get_or_create_profile(db, user)
    token = create_new_token(db, user)
    return AuthResponse(message="Login successful.", token=token.key, user=profile_out(profile))

@router.get("/profile/", response_model=UserProfileOut)
def profile(user: AuthUser = Depends(get_current_user), db: Session = Depends(get_db)):
    return profile_out(get_or_create_profile(db, user))

@router.post("/logout/")
def logout(
    request: Request,
    db: Session = Depends(get_db),
):
    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication credentials were not provided."
        )

    if authorization.startswith("Token "):
        key = authorization.split(" ", 1)[1].strip()
    else:
        key = authorization.strip()

    token = db.query(AuthToken).filter(AuthToken.key == key).first()

    if not token:
        raise HTTPException(status_code=401, detail="Invalid token.")

    db.delete(token)
    db.commit()

    return {"message": "Logout successful. Token deleted."}
