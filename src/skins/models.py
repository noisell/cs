import enum
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base, str256, intPK


class SkinQuality(enum.Enum):
    BS = "BS"  # Закалённый в боях
    WW = "WW"  # Поношенный
    FT = "FT"  # После полевых испытаний
    MW = "MW"  # Немного поношенный
    FN = "FN"  # Прямо с завода


class Gun(Base):
    __tablename__ = "gun"
    id: Mapped[intPK]
    name: Mapped[str256]
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("gun.id"), nullable=True)

    parent: Mapped[Optional["Gun"]] = relationship(back_populates="children", remote_side="gun.id")
    children: Mapped[Optional[list["Gun"]]] = relationship(back_populates="parent", cascade="all, delete-orphan")
    skins: Mapped[Optional[list["Skin"]]] = relationship(back_populates="gun")


class Skin(Base):
    __tablename__ = "skin"
    id: Mapped[intPK]
    name: Mapped[str256]
    price: Mapped[float]
    gun_id: Mapped[int] = mapped_column(ForeignKey("gun.id", ondelete="CASCADE", onupdate="CASCADE"))
    quality: Mapped[SkinQuality]
    active: Mapped[bool] = mapped_column(server_default="true")

    gun: Mapped[Gun] = relationship(back_populates="skins")
    users: Mapped[Optional[list["UserSkin"]]] = relationship(back_populates="skins")
    cases: Mapped[list["Case"]] = relationship(back_populates="skin")
