import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base, str256, time, intPK


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str256]
    username: Mapped[str256 | None] = mapped_column(server_default=None)
    referrer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('user.id'), server_default=None)
    photo_url: Mapped[str | None] = mapped_column(server_default=None)
    trade_url: Mapped[str | None] = mapped_column(server_default=None)
    balance_coin: Mapped[int] = mapped_column(server_default='0')
    balance_usdt: Mapped[float] = mapped_column(server_default='0')
    count_clip: Mapped[int] = mapped_column(server_default='5')
    time_zone: Mapped[int] = mapped_column(server_default='3')
    admin_level: Mapped[int] = mapped_column(server_default='0')
    created_at: Mapped[time]

    bets: Mapped[Optional[List["Bet"]]] = relationship(back_populates="user")


class UserBanned(Base):
    __tablename__ = 'user_banned'
    id: Mapped[intPK]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'))
    time_end: Mapped[datetime.datetime | None]
    message: Mapped[str]
    active: Mapped[bool] = mapped_column(server_default='true')
    created_at: Mapped[time]


class UserSkin(Base):
    __tablename__ = 'user_skin'
    id: Mapped[intPK]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'))
    skin_id: Mapped[int] = mapped_column(ForeignKey('skin.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at: Mapped[time]

    skin: Mapped["Skin"] = relationship(back_populates="users")


class UserCase(Base):
    __tablename__ = 'user_case'
    id: Mapped[intPK]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'))
    case_skin_id: Mapped[int] = mapped_column(ForeignKey('case_skin.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at: Mapped[time]


# Вывод скинов