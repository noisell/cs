import enum
from typing import Optional, List

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, intPK

class PromoType(enum.Enum):
    usdt = "usdt"
    coin = "coin"
    clip = "clip"


class Admin(Base):
    __tablename__ = 'admin'
    id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'), primary_key=True, autoincrement=False)
    level: Mapped[int] = mapped_column(server_default='1')
    password: Mapped[str]
    salt: Mapped[str]


class PromoCode(Base):
    __tablename__ = 'promo_code'
    id: Mapped[intPK]
    name: Mapped[str]
    type: Mapped[PromoType]
    value: Mapped[int]
    count: Mapped[int]

    users: Mapped[Optional[List["UserPromoCode"]]] = relationship(back_populates="promo_code")


class System(Base):
    __tablename__ = 'system'
    id: Mapped[intPK]
    name: Mapped[str]
    value: Mapped[str]
