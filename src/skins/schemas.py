from pydantic import BaseModel, Field

from src.skins.models import SkinQuality


class Skin(BaseModel):
    id: int = Field(description="id", title="")
    name: str = Field(description="Название", title="")
    price: float = Field(description="Цена", title="")
    gun_id: int = Field(description="id оружия", title="")
    quality: SkinQuality = Field(description="Качество", title="")