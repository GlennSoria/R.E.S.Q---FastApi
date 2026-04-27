from fastapi import HTTPException, Depends, Query
from sqlalchemy.orm import Session
from .database import get_db
from .models import AuthToken, AuthUser


def get_current_user(
    token: str | None = Query(default=None, description="Paste your login token here"),
    db: Session = Depends(get_db)
) -> AuthUser:

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication credentials were not provided."
        )

    key = token.strip()

    if key.startswith("Token "):
        key = key.split(" ", 1)[1].strip()

    auth_token = db.query(AuthToken).filter(AuthToken.key == key).first()

    if not auth_token or not auth_token.user or not auth_token.user.is_active:
        raise HTTPException(status_code=401, detail="Invalid token.")

    return auth_token.user