from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from src.bets.models import Currency, BetType


class CreateTeam(BaseModel):
    name: str = Field(description="Название", title="")
    logo_url: str = Field(description="Ссылка на логотип", title="")


class TeamScheme(CreateTeam):
    id: int = Field(description="id", title="")


class EventTeamScheme(BaseModel):
    id: int = Field(description="id команды в событии", title="")
    score: int = Field(description="Счет у данной команды", title="")
    total_coin: int = Field(description="Общее кол-во поставленных монет", title="")
    total_usdt: int = Field(description="Общее кол-во поставленных usdt", title="")
    team: TeamScheme = Field(description="Информация про команду", title="")

class EventAddScheme(BaseModel):
    date_start: datetime = Field(description="Дата начала", title="")
    team_one_id: int = Field(description="id первой команды", title="")
    team_two_id: int = Field(description="id второй команды", title="")


class EventScheme(BaseModel):
    id: int = Field(description="id", title="")
    date_start: datetime = Field(description="Дата начала", title="")
    status: bool = Field(description="Статус", title="")
    created_at: datetime = Field(description="Дата создания", title="")
    won: int | None = Field(description="Победившая команда", title="")
    won_first_map: int | None = Field(description="Победившая команда в первой карте", title="")
    won_second_map: int | None = Field(description="Победившая команда во второй карте", title="")
    dry_bill: bool | None = Field(description="Был ли сухой счет?", title="")
    knife: bool | None = Field(description="Был ли нож?", title="")
    teams: List[EventTeamScheme] = Field(description="Команды, которые участвуют в событии. Их всегда две", title="")


class BetScheme(BaseModel):
    user_id: int = Field(description="id пользователя", title="")
    event_team_id: int | None = Field(description="id команды в событии, на которую сделана ставка", title="")
    bet_type: BetType = Field(description="Тип ставки", title="")
    bet: bool = Field(description="Ставка", title="")
    currency: Currency = Field(description="Валюта", title="")
    amount: int = Field(description="Сумма", title="")


class EventFullScheme(EventScheme):
    bets: List[BetScheme]


class BetSimpleScheme(BaseModel):
    id: int = Field(description="id ставки", title="")
    event_team_id: int | None = Field(description="id команды в событии, на которую сделана ставка", title="")
    bet_type: BetType = Field(description="Тип ставки", title="")
    bet: bool = Field(description="Значение ставки. Для типа win возвращается только true", title="")
    currency: Currency = Field(description="В какой валюте ставка", title="")
    amount: int = Field(description="Сумма ставки", title="")
    active: bool = Field(description="Активна ли ставка", title="")
    event: EventScheme = Field(description="Информация про событие", title="")


class BetScheme(BetSimpleScheme):
    created_at: datetime = Field(description="Дата создания ставки", title="")


class BetCreateScheme(BaseModel):
    event_id: int = Field(description="id события", title="")
    event_team_id: int | None = Field(description="id команды в событии", title="")
    bet_type: BetType = Field(description="Тип ставки", title="")
    bet: bool = Field(description="Значение ставки. Для типа win принимается только true", title="")
    currency: Currency = Field(description="В какой валюте ставка", title="")
    amount: int = Field(description="Сумма ставки", title="")


class BetCreateSchemeResponse(BaseModel):
    id: int = Field(description="id сделанной ставки", title="")