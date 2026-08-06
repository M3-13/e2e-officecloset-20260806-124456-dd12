import os
import os.path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from models import ClothingItem, User
from schemas import ItemOut

UPLOADS_DIR = os.path.realpath("uploads")
MAX_IMAGE_SIZE = 5 * 1024 * 1024

MAGIC_SIGNATURES: list[tuple[bytes, str]] = [
    (b"\xff\xd8\xff", ".jpg"),
    (b"\x89PNG\r\n\x1a\n", ".png"),
]

WEBP_RIFF = b"RIFF"
WEBP_WEBP = b"WEBP"


def _check_magic_bytes(data: bytes) -> str | None:
    if len(data) < 12:
        return None
    for magic, ext in MAGIC_SIGNATURES:
        if data[: len(magic)] == magic:
            return ext
    if data[:4] == WEBP_RIFF and data[8:12] == WEBP_WEBP:
        return ".webp"
    return None


def _build_image_url(filename: str | None) -> str | None:
    if filename is None:
        return None
    return f"/api/wardrobe/images/{filename}"


def _item_to_out(item: ClothingItem) -> ItemOut:
    return ItemOut(
        id=item.id,
        name=item.name,
        category=item.category,
        color=item.color,
        notes=item.notes,
        image_url=_build_image_url(item.image_filename),
        created_at=item.created_at,
    )


def _save_image(image_file: UploadFile) -> str:
    data = image_file.file.read(16)
    image_file.file.seek(0)

    ext = _check_magic_bytes(data)
    if ext is None:
        raise ValueError("Only JPEG, PNG and WebP images are accepted")

    image_file.file.seek(0, os.SEEK_END)
    size = image_file.file.tell()
    image_file.file.seek(0)
    if size > MAX_IMAGE_SIZE:
        raise OverflowError("File exceeds 5 MB limit")

    filename = uuid4().hex + ext
    filepath = os.path.join(UPLOADS_DIR, filename)
    with open(filepath, "wb") as f:
        while chunk := image_file.file.read(1024 * 64):
            f.write(chunk)

    return filename


def _delete_image(filename: str) -> None:
    filepath = os.path.join(UPLOADS_DIR, filename)
    real = os.path.realpath(filepath)
    if not real.startswith(UPLOADS_DIR + os.sep):
        return
    if os.path.isfile(real):
        os.remove(real)


def create_item(
    db: Session,
    user: User,
    name: str,
    category: str,
    color: str | None = None,
    notes: str | None = None,
    image_file: UploadFile | None = None,
) -> ClothingItem:
    image_filename: str | None = None
    if image_file is not None and image_file.filename:
        image_filename = _save_image(image_file)

    item = ClothingItem(
        user_id=user.id,
        name=name,
        category=category,
        color=color,
        notes=notes,
        image_filename=image_filename,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_items(
    db: Session,
    user: User,
    category_filter: str | None = None,
) -> list[ItemOut]:
    query = db.query(ClothingItem).filter(ClothingItem.user_id == user.id)
    if category_filter is not None:
        query = query.filter(ClothingItem.category == category_filter)
    items = query.order_by(ClothingItem.created_at.desc()).all()
    return [_item_to_out(item) for item in items]


def get_item(db: Session, user: User, item_id: int) -> ItemOut:
    item = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == item_id, ClothingItem.user_id == user.id)
        .first()
    )
    if item is None:
        raise LookupError("Item not found")
    return _item_to_out(item)


def update_item(
    db: Session,
    user: User,
    item_id: int,
    name: str | None = None,
    category: str | None = None,
    color: str | None = None,
    notes: str | None = None,
    image_file: UploadFile | None = None,
) -> ItemOut:
    item = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == item_id, ClothingItem.user_id == user.id)
        .first()
    )
    if item is None:
        raise LookupError("Item not found")

    if name is not None:
        item.name = name
    if category is not None:
        item.category = category
    if color is not None:
        item.color = color
    if notes is not None:
        item.notes = notes

    if image_file is not None and image_file.filename:
        new_filename = _save_image(image_file)
        if item.image_filename is not None:
            _delete_image(item.image_filename)
        item.image_filename = new_filename

    db.commit()
    db.refresh(item)
    return _item_to_out(item)


def delete_item(db: Session, user: User, item_id: int) -> None:
    item = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == item_id, ClothingItem.user_id == user.id)
        .first()
    )
    if item is None:
        raise LookupError("Item not found")

    if item.image_filename is not None:
        _delete_image(item.image_filename)
    db.delete(item)
    db.commit()
