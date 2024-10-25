import enum
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.cases.models import TypePriceCase
from src.skins.schemas import SkinSimpleScheme


class SortingCase(enum.Enum):
    free = "free"
    paid = "paid"


class CaseAddScheme(BaseModel):
    name: str = Field(description="Название", title="")
    photo_url: str = Field(description="Ссылка на фото", title="")
    type_price: TypePriceCase = Field(description="Тип цены", title="")
    price: float = Field(description="Цена", title="")


class CaseGetScheme(CaseAddScheme):
    id: int = Field(description="id", title="")


class CasesGetAllScheme(BaseModel):
    id: int = Field(description="id", title="")
    name: str = Field(description="Название", title="")
    photo_url: str = Field(description="Ссылка на фото", title="")
    type_price: TypePriceCase = Field(description="Тип цены", title="")
    price: float = Field(description="Цена", title="")


class CaseSkinGetFullScheme(BaseModel):
    id: int = Field(description="id скина в кейсе", title="")
    chance: int = Field(description="Шанс на выпадение этого скина", title="")
    skin: SkinSimpleScheme = Field(description="Информация про скин", title="")


class CaseAndSkinsScheme(CaseGetScheme):
    skins: Optional[List[CaseSkinGetFullScheme]] = Field(description="Скины в кейсе")


class CaseSkinForAdminScheme(CaseSkinGetFullScheme):
    case: CasesGetAllScheme = Field(description="Информация про кейс")


class OpenCase(BaseModel):
    id: int = Field(description="id", title="")


class DateOpenCase(BaseModel):
    seconds: int = Field(description="Кол-во секунд через которое можно открыть кейс", title="")


class CaseSkinChangeScheme(BaseModel):
    id: int = Field(description="id скина в кейсе", title="")
    chance: int = Field(description="Шанс на выпадение этого скина", title="")