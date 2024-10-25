import enum
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import List

from src.database import Base, str256, intPK


class TypePriceCase(enum.Enum):
    friend = "friend"  # За друзей
    coin = "coin"  # За монетки
    usdt = "usdt"  # За usdt


class Case(Base):
    __tablename__ = "case"
    id: Mapped[intPK]
    name: Mapped[str256]
    photo_url: Mapped[str256] = mapped_column(server_default='https://457727d0-3339-4a3e-9814-ff011bb0a036.selstorage.ru/case.png')
    type_price: Mapped[TypePriceCase]
    price: Mapped[float]

    skins: Mapped[Optional[List["CaseSkin"]]] = relationship(back_populates="case")


class CaseSkin(Base):
    __tablename__ = "case_skin"
    id: Mapped[intPK]
    case_id: Mapped[int] = mapped_column(ForeignKey("case.id", ondelete="CASCADE", onupdate="CASCADE"))
    skin_id: Mapped[int] = mapped_column(ForeignKey("skin.id", ondelete="CASCADE", onupdate="CASCADE"))
    chance: Mapped[int]

    case: Mapped["Case"] = relationship(back_populates="skins")
    skin: Mapped["Skin"] = relationship(back_populates="cases")
    users: Mapped[Optional[List["UserCase"]]] = relationship(back_populates="case_skin")
