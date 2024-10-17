from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from src.bets.models import Currency, BetType, EventStatus


class TeamScheme(BaseModel):
    id: int = Field(description="id", title="")
    name: str = Field(description="Название", title="")
    logo_url: str = Field(description="Ссылка на логотип", title="")

class EventScheme(BaseModel):
    id: int = Field(description="id", title="")
    date_start: datetime = Field(description="Дата начала", title="")
    status: EventStatus = Field(description="Статус", title="")
    created_at: datetime = Field(description="Дата создания", title="")


class EventTeamScheme(BaseModel):
    id: int = Field(description="id команды в событии", title="")
    score: int = Field(description="Счет у данной команды", title="")
    total_coin: int = Field(description="Общее кол-во поставленных монет", title="")
    total_usdt: int = Field(description="Общее кол-во поставленных usdt", title="")
    team: TeamScheme = Field(description="Информация про команду", title="")


class BetSimpleScheme(BaseModel):
    bet_type: BetType = Field(description="Тип ставки", title="")
    bet: bool = Field(description="Ставка. Для типа win принимается и возвращается только true", title="")
    currency: Currency = Field(description="В какой валюте ставка", title="")
    amount: int = Field(description="Сумма ставки", title="")
    active: bool = Field(description="Активна ли ставка", title="")
    event_team: List[EventTeamScheme] = Field(description="Команды, которые участвуют в событии", title="")
    event: EventScheme = Field(description="Информация про событие", title="")