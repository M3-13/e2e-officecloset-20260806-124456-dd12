from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from models import ClothingItem, Outfit, OutfitItem, User
from schemas import ItemOut, OutfitOut


def _to_item_out(item: ClothingItem) -> ItemOut:
    image_url: str | None = None
    if item.image_filename:
        image_url = f"/api/wardrobe/images/{item.image_filename}"
    return ItemOut(
        id=item.id,
        name=item.name,
        category=item.category,
        color=item.color,
        notes=item.notes,
        image_url=image_url,
        created_at=item.created_at,
    )


def _to_outfit_out(outfit: Outfit) -> OutfitOut:
    items = [
        _to_item_out(oi.clothing_item)
        for oi in sorted(outfit.outfit_items, key=lambda oi: oi.position)
    ]
    return OutfitOut(
        id=outfit.id,
        name=outfit.name,
        items=items,
        created_at=outfit.created_at,
    )


def _validate_and_resolve_items(db: Session, user: User, item_ids: list[int]) -> list[ClothingItem]:
    if not item_ids:
        return []
    items = (
        db.query(ClothingItem)
        .filter(ClothingItem.id.in_(item_ids), ClothingItem.user_id == user.id)
        .all()
    )
    found_ids = {item.id for item in items}
    for iid in item_ids:
        if iid not in found_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Item {iid} is invalid or does not belong to you",
            )
    id_to_item = {item.id: item for item in items}
    return [id_to_item[iid] for iid in item_ids]


def create_outfit(db: Session, user: User, name: str, item_ids: list[int]) -> Outfit:
    items = _validate_and_resolve_items(db, user, item_ids)

    outfit = Outfit(name=name, user_id=user.id)
    db.add(outfit)
    db.flush()

    for position, item in enumerate(items):
        oi = OutfitItem(outfit_id=outfit.id, clothing_item_id=item.id, position=position)
        db.add(oi)

    db.commit()
    db.refresh(outfit)
    return outfit


def get_outfits(db: Session, user: User) -> list[OutfitOut]:
    outfits = (
        db.query(Outfit)
        .filter(Outfit.user_id == user.id)
        .options(joinedload(Outfit.outfit_items).joinedload(OutfitItem.clothing_item))
        .order_by(Outfit.created_at.desc())
        .all()
    )
    return [_to_outfit_out(o) for o in outfits]


def get_outfit(db: Session, user: User, outfit_id: int) -> OutfitOut:
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.user_id == user.id)
        .options(joinedload(Outfit.outfit_items).joinedload(OutfitItem.clothing_item))
        .first()
    )
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit not found")
    return _to_outfit_out(outfit)


def update_outfit(
    db: Session,
    user: User,
    outfit_id: int,
    name: str | None = None,
    item_ids: list[int] | None = None,
) -> OutfitOut:
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == user.id).first()
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit not found")

    if name is not None:
        outfit.name = name

    if item_ids is not None:
        items = _validate_and_resolve_items(db, user, item_ids)
        db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit_id).delete()
        for position, item in enumerate(items):
            oi = OutfitItem(outfit_id=outfit_id, clothing_item_id=item.id, position=position)
            db.add(oi)

    db.commit()
    db.refresh(outfit)
    return _to_outfit_out(outfit)


def delete_outfit(db: Session, user: User, outfit_id: int) -> None:
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == user.id).first()
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit not found")
    db.delete(outfit)
    db.commit()
