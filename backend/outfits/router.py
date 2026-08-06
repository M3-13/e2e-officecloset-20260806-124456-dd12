from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models import User

router = APIRouter(prefix="/api/outfits", tags=["outfits"])


@router.get("", status_code=501)
async def list_outfits(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    raise HTTPException(status_code=501, detail="outfits #1 implements this")


@router.post("", status_code=501)
async def create_outfit(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    raise HTTPException(status_code=501, detail="outfits #1 implements this")


@router.get("/{id}", status_code=501)
async def get_outfit(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    raise HTTPException(status_code=501, detail="outfits #1 implements this")


@router.put("/{id}", status_code=501)
async def update_outfit(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    raise HTTPException(status_code=501, detail="outfits #1 implements this")


@router.delete("/{id}", status_code=501)
async def delete_outfit(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    raise HTTPException(status_code=501, detail="outfits #1 implements this")
