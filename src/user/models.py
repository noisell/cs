import datetime
import enum
from typing import Optional, List

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.cases.models import CaseSkin
from src.database import Base, str256, time, intPK


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str256]
    username: Mapped[str256 | None] = mapped_column(server_default=None)
    referrer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('user.id'), server_default=None)
    photo_url: Mapped[str | None] = mapped_column(server_default=None)
    trade_url: Mapped[str | None] = mapped_column(server_default=None)
    use_ref_bonus: Mapped[bool | None] = mapped_column(server_default=None)
    balance_coin: Mapped[int] = mapped_column(server_default='0')
    balance_usdt: Mapped[float] = mapped_column(server_default='0')
    balance_referrers: Mapped[int] = mapped_column(server_default='0')
    count_clip: Mapped[int] = mapped_column(server_default='5')
    time_zone: Mapped[int] = mapped_column(server_default='3')
    banned: Mapped[bool] = mapped_column(server_default='false')
    last_open_case: Mapped[time | None] = mapped_column(server_default=None)
    created_at: Mapped[time]

    bets: Mapped[Optional[List["Bet"]]] = relationship(back_populates="user")
    skins: Mapped[Optional[List["UserSkin"]]] = relationship(back_populates="user")
    cases: Mapped[Optional[List["UserCase"]]] = relationship(back_populates="user")
    moneys: Mapped[Optional[List["UserMoney"]]] = relationship(back_populates="user")
    receiving_skin: Mapped[Optional[List["UserReceivingSkin"]]] = relationship(back_populates="user")
    parent: Mapped[Optional["User"]] = relationship(back_populates="referrers", remote_side="User.id")
    referrers: Mapped[Optional[List["User"]]] = relationship(back_populates="parent", cascade="all, delete-orphan")


class UserSkin(Base):
    __tablename__ = 'user_skin'
    id: Mapped[intPK]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'))
    skin_id: Mapped[int] = mapped_column(ForeignKey('skin.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at: Mapped[time]

    skin: Mapped["Skin"] = relationship(back_populates="users")
    user: Mapped["User"] = relationship(back_populates="skins")


class UserCase(Base):
    __tablename__ = 'user_case'
    id: Mapped[intPK]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'))
    case_skin_id: Mapped[int] = mapped_column(ForeignKey('case_skin.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at: Mapped[time]

    case_skin: Mapped["CaseSkin"] = relationship(back_populates="users")
    user: Mapped["User"] = relationship(back_populates="cases")


class UserPromoCode(Base):
    __tablename__ = 'user_promo_code'
    id: Mapped[intPK]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'))
    promo_code_id: Mapped[int] = mapped_column(ForeignKey('promo_code.id'))

    promo_code: Mapped["PromoCode"] = relationship(back_populates="users")


class UserMoney(Base):
    __tablename__ = 'user_money'
    id: Mapped[intPK]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'))
    amount: Mapped[float]
    created_at: Mapped[time]

    user: Mapped["User"] = relationship(back_populates="moneys")


class UserReceivingSkin(Base):
    __tablename__ = 'user_receiving_skin'
    id: Mapped[intPK]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'))
    skin_id: Mapped[int] = mapped_column(ForeignKey('skin.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at: Mapped[time]
    status: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="receiving_skin")
    skin: Mapped["Skin"] = relationship(back_populates="receiving_skins")

# Вывод скинов