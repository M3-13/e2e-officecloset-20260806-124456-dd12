from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    auth_header: str | None = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token: str = auth_header[len("Bearer ") :]
    try:
        payload: dict = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    sub: str | None = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="Token missing subject claim")
    try:
        user_id: int = int(sub)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token subject") from exc

    user: User | None = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def create_access_token(user_id: int) -> str:
    expire: datetime = datetime.now(UTC) + timedelta(hours=24)
    payload: dict = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
