import os
import os.path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models import User
from schemas import CategoryEnum, ItemOut
from wardrobe.service import (
    UPLOADS_DIR,
    create_item,
    delete_item,
    get_item,
    get_items,
    update_item,
)

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])


@router.get("/items", response_model=list[ItemOut])
async def list_items(
    request: Request,
    category: CategoryEnum | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ItemOut]:
    return get_items(
        db=db,
        user=current_user,
        category_filter=category.value if category else None,
    )


@router.post("/items", response_model=ItemOut, status_code=201)
async def create_item_route(
    request: Request,
    name: str = Form(...),
    category: CategoryEnum = Form(...),
    color: str | None = Form(None),
    notes: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    try:
        item = create_item(
            db=db,
            user=current_user,
            name=name,
            category=category.value,
            color=color,
            notes=notes,
            image_file=image,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OverflowError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    return ItemOut(
        id=item.id,
        name=item.name,
        category=item.category,
        color=item.color,
        notes=item.notes,
        image_url=(f"/api/wardrobe/images/{item.image_filename}" if item.image_filename else None),
        created_at=item.created_at,
    )


@router.get("/items/{id}", response_model=ItemOut)
async def get_item_route(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    try:
        return get_item(db=db, user=current_user, item_id=id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/items/{id}", response_model=ItemOut)
async def update_item_route(
    id: int,
    request: Request,
    name: str | None = Form(None),
    category: CategoryEnum | None = Form(None),
    color: str | None = Form(None),
    notes: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    try:
        return update_item(
            db=db,
            user=current_user,
            item_id=id,
            name=name,
            category=category.value if category else None,
            color=color,
            notes=notes,
            image_file=image,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OverflowError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc


@router.delete("/items/{id}", status_code=204)
async def delete_item_route(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        delete_item(db=db, user=current_user, item_id=id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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
