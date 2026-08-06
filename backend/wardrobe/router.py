import os
import os.path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models import User

UPLOADS_DIR = os.path.realpath("uploads")

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])


@router.get("/items", status_code=501)
async def list_items(
    request: Request,
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")


@router.post("/items", status_code=501)
async def create_item(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")


@router.get("/items/{id}", status_code=501)
async def get_item(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")


@router.put("/items/{id}", status_code=501)
async def update_item(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")


@router.delete("/items/{id}", status_code=501)
async def delete_item(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")


@router.get("/images/{filename}")
async def get_image(
    filename: str,
    request: Request,
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    safe_name = os.path.basename(filename)
    if not safe_name or safe_name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    filepath = os.path.realpath(os.path.join(UPLOADS_DIR, safe_name))
    if not filepath.startswith(UPLOADS_DIR + os.sep):
        raise HTTPException(status_code=404, detail="Image not found")
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath)
