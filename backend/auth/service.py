from sqlalchemy.orm import Session

from models import User
from schemas import Token, UserCreate, UserOut


def register(db: Session, data: UserCreate) -> User:
    raise NotImplementedError("auth #6 implements this")


def login(db: Session, data: UserCreate) -> Token:
    raise NotImplementedError("auth #6 implements this")


def get_me(user: User) -> UserOut:
    raise NotImplementedError("auth #6 implements this")


def delete_account(db: Session, user: User) -> None:
    raise NotImplementedError("auth #6 implements this")
