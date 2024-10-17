import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base, str256, intPK, time


class EventStatus(enum.Enum):
    active = "active"
    winner_one = "winner_one"
    winner_two = "winner_two"


class BetType(enum.Enum):
    win = "win"
    dry_bill = "dry_bill"
    winner_first_card = "winner_first_card"
    winner_second_card = "winner_second_card"
    knife = "knife"


class Currency(enum.Enum):
    coin = "coin"
    usdt = "usdt"


class Team(Base):
    __tablename__ = "team"
    id: Mapped[intPK]
    name: Mapped[str256]
    logo_url: Mapped[str256] = mapped_column(server_default='https://457727d0-3339-4a3e-9814-ff011bb0a036.selstorage.ru/team.svg')

    events: Mapped[List["EventTeam"]] = relationship(back_populates="team")


class Event(Base):
    __tablename__ = "event"
    id: Mapped[intPK]
    date_start: Mapped[datetime]
    status: Mapped[EventStatus] = mapped_column(server_default='active')
    created_at: Mapped[time]

    teams: Mapped[List["EventTeam"]] = relationship(back_populates="event")
    bets: Mapped[List["Bet"]] = relationship(back_populates="event")


class EventTeam(Base):
    __tablename__ = "event_team"
    id: Mapped[intPK]
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))
    score: Mapped[int] = mapped_column(server_default='0')
    total_coin: Mapped[int] = mapped_column(server_default='0')
    total_usdt: Mapped[int] = mapped_column(server_default='0')

    event: Mapped["Event"] = relationship(back_populates="teams")
    team: Mapped["Team"] = relationship(back_populates="events")
    bets: Mapped[Optional[List["Bet"]]] = relationship(back_populates="event_team")


class Bet(Base):
    __tablename__ = "bet"
    id: Mapped[intPK]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    event_team_id: Mapped[int] = mapped_column(ForeignKey("event_team.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"))
    bet_type: Mapped[BetType]
    bet: Mapped[bool]
    currency: Mapped[Currency]
    amount: Mapped[int]
    active: Mapped[bool] = mapped_column(server_default='true')

    event: Mapped["Event"] = relationship(back_populates="bets")
    event_team: Mapped["EventTeam"] = relationship(back_populates="bets")
    user: Mapped["User"] = relationship(back_populates="bets")
