from fastapi import HTTPException, Depends, Query, Request
from sqlalchemy.orm import Session
from .database import get_db
from .models import AuthToken, AuthUser


def get_current_user(
    request: Request,
    token: str | None = Query(default=None, description="Paste your login token here"),
    db: Session = Depends(get_db)
) -> AuthUser:

    key = None

    # PowerShell / frontend header
    authorization = request.headers.get("Authorization")

    if authorization:
        if authorization.startswith("Token "):
            key = authorization.split(" ", 1)[1].strip()
        else:
            key = authorization.strip()

    # Swagger /docs single input
    elif token:
        if token.startswith("Token "):
            key = token.split(" ", 1)[1].strip()
        else:
            key = token.strip()

    if not key:
        raise HTTPException(
            status_code=401,
            detail="Authentication credentials were not provided."
        )

    auth_token = db.query(AuthToken).filter(AuthToken.key == key).first()

    if not auth_token or not auth_token.user or not auth_token.user.is_active:
        raise HTTPException(status_code=401, detail="Invalid token.")

    return auth_token.user