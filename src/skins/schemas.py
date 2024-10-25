import enum
from typing import Any

from pydantic import BaseModel, Field

from src.skins.models import SkinQuality, RaritySkin

class Sorting(enum.Enum):
    popular = "popular"
    cheaper = "cheaper"
    dearly = "dearly"


class SkinCreateScheme(BaseModel):
    name: str = Field(description="Название", title="")
    price: float = Field(description="Цена", title="")
    gun_id: int = Field(description="id оружия", title="")
    quality: SkinQuality = Field(description="Качество", title="")
    rarity: RaritySkin = Field(description="Редкость", title="")
    image_url: str = Field(description="Ссылка на изображение", title="")


class SkinSimpleScheme(SkinCreateScheme):
    id: int = Field(description="id скина", title="")


class SkinFullScheme(SkinCreateScheme):
    id: int = Field(description="id скина", title="")
    active: bool = Field(description="Активный ли скин", title="")


class SearchSkinScheme(BaseModel):
    id: int = Field(description="id скина", title="")
    name: str = Field(description="Название скина", title="")


class GunsScheme(BaseModel):
    id: int = Field(description="id оружия", title="")
    name: str = Field(description="Название оружия", title="")
    children: list[dict[str, Any]] | None = Field(None, description="Дочерние оружия", title="")


class GunsFullScheme(GunsScheme):
    parent_id: int | None = Field(description="id родительской категории оружия", title="")


class BuySkinScheme(BaseModel):
    id: int = Field(description="id скина", title="")


class GunScheme(BaseModel):
    name: str = Field(description="Название оружия", title="")
    parent_id: int | None = Field(None, description="id родительской категории оружия")


class GunGetScheme(GunScheme):
    id: int = Field(description="id оружия", title="")


class ResSkinScheme(BaseModel):
    id: int = Field(description="id скина", title="")


class StatusRes(enum.Enum):
    success = "success"
    not_found_trade_url = "not_found_trade_url"
    no_validated_trade_url = "no_validated_trade_url"
    not_found_skin = "not_found_skin"
    no_skins = "no_skins"
    no_money = "no_money"
    didnt_buy = "didnt_buy"
    unknown_error = "unknown_error"


class ResSkinResponseScheme(BaseModel):
    status: StatusRes = Field(description="Статус вывода. Успех - success, все остальное ошибки.", title="")