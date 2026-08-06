from sqlalchemy.orm import Session

from models import User
from schemas import ItemCreate, ItemOut


def list_items(db: Session, user: User, category: str | None = None) -> list[ItemOut]:
    raise NotImplementedError("wardrobe #4 implements this")


def create_item(
    db: Session, user: User, data: ItemCreate, image_data: bytes | None = None
) -> ItemOut:
    raise NotImplementedError("wardrobe #4 implements this")


def get_item(db: Session, user: User, item_id: int) -> ItemOut:
    raise NotImplementedError("wardrobe #4 implements this")


def update_item(
    db: Session, user: User, item_id: int, data: dict, image_data: bytes | None = None
) -> ItemOut:
    raise NotImplementedError("wardrobe #4 implements this")


def delete_item(db: Session, user: User, item_id: int) -> None:
    raise NotImplementedError("wardrobe #4 implements this")
