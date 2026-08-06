import contextlib
import os

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth.dependencies import create_access_token
from models import ClothingItem, User
from schemas import Token, UserCreate, UserOut

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
UPLOAD_DIR = "uploads"


def register(db: Session, data: UserCreate) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=data.email, hashed_password=pwd_context.hash(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from exc
    db.refresh(user)
    return user


def login(db: Session, data: UserCreate) -> Token:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(user.id)
    return Token(access_token=access_token, token_type="bearer")


def get_me(user: User) -> UserOut:
    return UserOut.model_validate(user)


def delete_account(db: Session, user: User) -> None:
    items_with_images = (
        db.query(ClothingItem)
        .filter(
            ClothingItem.user_id == user.id,
            ClothingItem.image_filename.isnot(None),
            ClothingItem.image_filename != "",
        )
        .all()
    )
    filenames = [item.image_filename for item in items_with_images if item.image_filename]

    db.delete(user)
    db.commit()

    for filename in filenames:
        with contextlib.suppress(OSError):
            os.remove(os.path.join(UPLOAD_DIR, filename))
