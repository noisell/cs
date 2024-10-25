from pydantic import BaseModel, Field

from src.admin.models import PromoType


class AdminScheme(BaseModel):
    id: int = Field(description="id", title="")
    level: int = Field(description="Уровень", title="")
    password: str = Field(description="Пароль", title="")
    salt: str = Field(description="Соль", title="")


class SimpleAdminScheme(BaseModel):
    user_id: int = Field(description="id в Telegram", title="")
    level: int = Field(description="Уровень. Число от 1 до 3. 1 - оператор, 2 - старший, 3 - владелец.", title="")


class SimpleTrueAdminScheme(BaseModel):
    id: int = Field(description="id в Telegram", title="")
    level: int = Field(description="Уровень. Число от 1 до 3. 1 - оператор, 2 - старший, 3 - владелец.", title="")

class StatusScheme(BaseModel):
    success: bool = Field(description="Успешно?", title="")

class IdScheme(BaseModel):
    id: int = Field(description="id", title="")


class EventTeamScheme(BaseModel):
    event_id: int = Field(description="id события", title="")
    event_team_one_id: int = Field(description="id первой команды в событии", title="")
    event_team_two_id: int = Field(description="id второй команды в событии", title="")


class ChangeScoreScheme(BaseModel):
    event_team_id: int = Field(description="id команды в событии", title="")
    score: int = Field(description="Новый счет")


class ChangeEvent(BaseModel):
    event_id: int = Field(description="id события", title="")
    won: int = Field(description="id команды, которая победила", title="")
    won_first_map: int = Field(description="id команды, которая победила первую карту", title="")
    won_second_map: int = Field(description="id команды, которая победила вторую карту", title="")
    dry_bill: bool = Field(description="Был ли сухой счет", title="")
    knife: bool = Field(description="Был ли нож", title="")


class CreatePromoCodeScheme(BaseModel):
    name: str = Field(description="Название промокода", title="")
    type: PromoType = Field(description="Тип промокода", title="")
    value: int = Field(description="Сколько дает промокод?", title="")
    count: int = Field(description="Кол-ва активаций", title="")


class PromoCodeScheme(CreatePromoCodeScheme):
    id: int = Field(description="id промокода", title="")


class InputPromoCodeScheme(BaseModel):
    name: str = Field(description="Название промокода", title="")


class CaseSkinAddScheme(BaseModel):
    case_id: int = Field(description="id кейса", title="")
    skin_id: int = Field(description="id скина", title="")
    chance: int = Field(description="Шанс выпадения скина", title="")


class StatisticsValuesScheme(BaseModel):
    value: int = Field(description="Значение")
    last_value: int = Field(description="Прошлое значение")
    percent: float = Field(description="Процент роста")


class CurrenStatisticsScheme(BaseModel):
    day: StatisticsValuesScheme = Field(description="За день", title="")
    month: StatisticsValuesScheme = Field(description="За месяц", title="")
    all: int = Field(description="За все время", title="")


class StatisticsScheme(BaseModel):
    users: CurrenStatisticsScheme = Field(description="Статистика по пользователям", title="")
    bets: CurrenStatisticsScheme = Field(description="Статистика по ставкам", title="")
    cases: CurrenStatisticsScheme = Field(description="Статистика по кейсам", title="")
    skins: CurrenStatisticsScheme = Field(description="Статистика по скинам", title="")


class BanScheme(BaseModel):
    user_id: int = Field(description="id пользователя", title="")
    value: bool = Field(description="Забанить - true, разбанить - false", title="")


class SystemScheme(BaseModel):
    market: str = Field(description="Токен от маркета", title="")
    ton: str = Field(description="Кошелек Ton", title="")


