from sqlalchemy.orm import Session

from models import User
from schemas import OutfitCreate, OutfitOut


def list_outfits(db: Session, user: User) -> list[OutfitOut]:
    raise NotImplementedError("outfits #1 implements this")


def create_outfit(db: Session, user: User, data: OutfitCreate) -> OutfitOut:
    raise NotImplementedError("outfits #1 implements this")


def get_outfit(db: Session, user: User, outfit_id: int) -> OutfitOut:
    raise NotImplementedError("outfits #1 implements this")


def update_outfit(db: Session, user: User, outfit_id: int, data: dict) -> OutfitOut:
    raise NotImplementedError("outfits #1 implements this")


def delete_outfit(db: Session, user: User, outfit_id: int) -> None:
    raise NotImplementedError("outfits #1 implements this")
