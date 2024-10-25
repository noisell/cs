import enum
from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base, str256, intPK


class SkinQuality(enum.Enum):
    BS = "BS"  # Закалённый в боях
    WW = "WW"  # Поношенный
    FT = "FT"  # После полевых испытаний
    MW = "MW"  # Немного поношенный
    FN = "FN"  # Прямо с завода


class RaritySkin(enum.Enum):
    CG = "CG"  # Ширпотреб
    IQ = "IQ"  # Промышленное качество
    AQ = "AQ"  # Армейское качество
    PR = "PR"  # Запрещенное
    CL = "CL"  # Засекреченное
    SE = "SE"  # Тайное
    CO = "CO"  # Крайне редкое


class Gun(Base):
    __tablename__ = "gun"
    id: Mapped[intPK]
    name: Mapped[str256]
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("gun.id"), nullable=True)

    parent: Mapped[Optional["Gun"]] = relationship(back_populates="children", remote_side="Gun.id")
    children: Mapped[Optional[list["Gun"]]] = relationship(back_populates="parent", cascade="all, delete-orphan")
    skins: Mapped[Optional[list["Skin"]]] = relationship(back_populates="gun")


class Skin(Base):
    __tablename__ = "skin"
    id: Mapped[intPK]
    name: Mapped[str256]
    price: Mapped[float]
    gun_id: Mapped[int] = mapped_column(ForeignKey("gun.id", ondelete="CASCADE", onupdate="CASCADE"))
    quality: Mapped[SkinQuality]
    rarity: Mapped[RaritySkin]
    image_url: Mapped[str]
    active: Mapped[bool] = mapped_column(server_default="true")

    gun: Mapped[Gun] = relationship(back_populates="skins")
    users: Mapped[Optional[List["UserSkin"]]] = relationship(back_populates="skin")
    cases: Mapped[Optional[List["CaseSkin"]]] = relationship(back_populates="skin")
    receiving_skins: Mapped[List["UserReceivingSkin"]] = relationship(back_populates="skin")
