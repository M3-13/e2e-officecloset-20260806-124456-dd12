from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models import User
from schemas import UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=501)
async def register(data: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    raise HTTPException(status_code=501, detail="auth #6 implements this")


@router.post("/login", status_code=501)
async def login(data: UserCreate, db: Session = Depends(get_db)) -> dict:
    raise HTTPException(status_code=501, detail="auth #6 implements this")


@router.get("/me", status_code=501)
async def get_me(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserOut:
    raise HTTPException(status_code=501, detail="auth #6 implements this")


@router.delete("/me", status_code=501)
async def delete_me(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    raise HTTPException(status_code=501, detail="auth #6 implements this")
