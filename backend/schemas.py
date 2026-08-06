from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class CategoryEnum(StrEnum):
    top = "top"
    bottom = "bottom"
    dress = "dress"
    shoes = "shoes"
    accessory = "accessory"


class ItemCreate(BaseModel):
    name: str
    category: CategoryEnum
    color: str | None = None
    notes: str | None = None


class ItemOut(BaseModel):
    id: int
    name: str
    category: str
    color: str | None = None
    notes: str | None = None
    image_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OutfitCreate(BaseModel):
    name: str
    item_ids: list[int]


class OutfitUpdate(BaseModel):
    name: str | None = None
    item_ids: list[int] | None = None


class OutfitOut(BaseModel):
    id: int
    name: str
    items: list[ItemOut]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
