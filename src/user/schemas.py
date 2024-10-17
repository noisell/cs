import datetime
import enum
from typing import List, Optional

from pydantic import BaseModel, Field

from src.bets.schemas import BetSimpleScheme
from src.skins.schemas import Skin


class UserAdd(BaseModel):
    id: int = Field(description="Id пользователя в Telegram", examples=["82321932"], title="")
    name: str = Field(description="Имя пользователя", examples=["Артемий"], title="")
    username: str | None = Field(None, description="Username пользователя в Telegram", examples=["noisell"], title="")
    referrer_id: int | None = Field(None, description="ID реферера", examples=["321342533"], title="")
    time_zone: str = Field(
        description="Часовой пояс IANA. Если значение будет переданной с ошибкой, по умолчанию будет Europe/Moscow",
        examples=["Europe/Moscow"], title="")


class UserSimpleGet(BaseModel):
    photo_url: str | None = Field(description="Фото профиля", title="")
    count_clip: int = Field(description="Кол-во обойм", title="")
    balance_coin: int = Field(description="Баланс монет", title="")
    balance_usdt: float = Field(description="Баланс USDT", title="")


class UserLevelAdminResponse(BaseModel):
    admin_level: int = Field(description="Уровень администратора", title="")

class UserUpdateFirstname(BaseModel):
    new_firstname: str = Field(description="Новое имя пользователя для БД", title="")


class UserStatistics(BaseModel):
    total_bets: int = Field(description="Общее кол-во ставок")
    total_skins: int = Field(description="Общее кол-во скинов")
    total_referrals: int = Field(description="Общее кол-во друзей")
    total_opened_cases: int = Field(description="Общее кол-во открытых кейсов")
    total_days_on_platform: int = Field(description="Общее кол-во дней на платформе")


class UserReferral(BaseModel):
    photo_url: str | None = Field(description="Фото профиля", title="")


class UserAllGet(BaseModel):
    statistics: UserStatistics = Field(description="Статистика", title="")
    referrals: Optional[List[UserReferral]] = Field(description="Рефералы", title="")
    skins: Optional[List[Skin]] = Field(description="Скины", title="")
    bets: Optional[List[BetSimpleScheme]] = Field(description="Ставки", title="")