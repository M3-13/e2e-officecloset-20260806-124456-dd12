from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from auth.service import delete_account, get_me, login, register
from database import get_db
from models import User
from schemas import Token, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=UserOut)
async def register_endpoint(data: UserCreate, db: Session = Depends(get_db)):
    user = register(db, data)
    return user


@router.post("/login", status_code=200, response_model=Token)
async def login_endpoint(data: UserCreate, db: Session = Depends(get_db)):
    return login(db, data)


@router.get("/me", status_code=200, response_model=UserOut)
async def get_me_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_me(current_user)


@router.delete("/me", status_code=204)
async def delete_me_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_account(db, current_user)
    return Response(status_code=204)
