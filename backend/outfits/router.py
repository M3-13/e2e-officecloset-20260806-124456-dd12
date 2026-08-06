from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models import User
from outfits import service as outfits_service
from schemas import OutfitCreate, OutfitOut, OutfitUpdate

router = APIRouter(prefix="/api/outfits", tags=["outfits"])


@router.get("", response_model=list[OutfitOut])
async def list_outfits(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[OutfitOut]:
    return outfits_service.get_outfits(db, current_user)


@router.post("", response_model=OutfitOut, status_code=201)
async def create_outfit(
    body: OutfitCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OutfitOut:
    outfit = outfits_service.create_outfit(db, current_user, body.name, body.item_ids)
    return outfits_service._to_outfit_out(outfit)


@router.get("/{id}", response_model=OutfitOut)
async def get_outfit(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OutfitOut:
    return outfits_service.get_outfit(db, current_user, id)


@router.put("/{id}", response_model=OutfitOut)
async def update_outfit(
    id: int,
    body: OutfitUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OutfitOut:
    return outfits_service.update_outfit(
        db, current_user, id, name=body.name, item_ids=body.item_ids
    )


@router.delete("/{id}", status_code=204)
async def delete_outfit(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    outfits_service.delete_outfit(db, current_user, id)
