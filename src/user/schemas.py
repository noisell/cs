import datetime
import enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from src.bets.schemas import BetSimpleScheme, BetScheme
from src.cases.schemas import CaseSkinForAdminScheme
from src.skins.schemas import SkinSimpleScheme


class UserAdd(BaseModel):
    id: int = Field(description="Id пользователя в Telegram", examples=["82321932"], title="")
    name: str = Field(description="Имя пользователя", examples=["Артемий"], title="")
    username: str | None = Field(None, description="Username пользователя в Telegram", examples=["noisell"], title="")
    referrer_id: int | None = Field(None, description="ID реферера", examples=["321342533"], title="")
    time_zone: str = Field(
        description="Часовой пояс IANA. Если значение будет переданной с ошибкой, по умолчанию будет Europe/Moscow",
        examples=["Europe/Moscow"], title="")


class UserGet(UserAdd):
    time_zone: int = Field(description="Смещение часового пояса", title="")
    photo_url: str | None = Field(description="Фото профиля", title="")
    trade_url: str | None = Field(description="Трейд ссылка", title="")
    use_ref_bonus: bool | None = Field(description="Использовался ли реферальный бонус", title="")
    count_clip: int = Field(description="Кол-во обойм", title="")
    balance_coin: int = Field(description="Баланс монет", title="")
    balance_usdt: float = Field(description="Баланс USDT", title="")
    balance_referrers: int = Field(description="Баланс рефералов", title="")
    last_open_case: datetime.datetime | None = Field(description="Дата открытия последнего кейса", title="")
    banned: bool = Field(description="Заблокирован ли пользователь?", title="")
    created_at: datetime.datetime = Field(description="Дата создания аккаунта", title="")


class UserSimpleGet(BaseModel):
    photo_url: str | None = Field(description="Фото профиля", title="")
    count_clip: int = Field(description="Кол-во обойм", title="")
    balance_coin: int = Field(description="Баланс монет", title="")
    balance_usdt: float = Field(description="Баланс USDT", title="")
    balance_referrers: int = Field(description="Баланс рефералов", title="")


class UserBannedResponse(BaseModel):
    banned: bool = Field(description="Забанен ли пользователь?", title="")

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
    skins: Optional[List[SkinSimpleScheme]] = Field(description="Скины", title="")
    bets: Optional[List[BetSimpleScheme]] = Field(description="Ставки", title="")


class TradeUrlScheme(BaseModel):
    trade_url: Union[str, None] = Field(description="Трейд ссылка пользователя", title="")

class AddUSDTScheme(BaseModel):
    value: int = Field(description="Кол-во", title="")


class ActivatePromoCode(BaseModel):
    activated: bool = Field(description="Активирован ли промокод?", title="", examples=[False])
    message: str = Field(description="Сообщение которое надо вывести пользователю", title="", examples=["Вы уже использовали этот промокод"])


class UserCaseScheme(BaseModel):
    id: int = Field(description="id записи", title="")
    created_at: datetime.datetime = Field(description="Дата создания", title="")
    case_skin: CaseSkinForAdminScheme = Field(description="Скин который выбил", title="")


class MoneyScheme(BaseModel):
    id: int = Field(description="id записи", title="")
    amount: float = Field(description="Сумма пополнения", title="")
    created_at: datetime.datetime = Field(description="Дата", title="")


class ReceivingSkinScheme(BaseModel):
    id: int = Field(description="id записи", title="")
    status: str = Field(description="Статус вывода", title="")
    created_at: datetime.datetime = Field(description="Дата", title="")
    skin: SkinSimpleScheme = Field(description="Информация про скин", title="")

class UserInfoReferral(BaseModel):
    id: int = Field(description="id пользователя", title="")
    name: str = Field(description="Имя пользователя", title="")
    photo_url: str | None = Field(description="Фото профиля", title="")

class UserFullInfoScheme(UserGet):
    statistics: UserStatistics = Field(description="Статистика", title="")
    skins: List[SkinSimpleScheme] = Field(description="Скины", title="")
    bets: List[BetSimpleScheme] = Field(description="Ставки", title="")
    cases: List[UserCaseScheme] = Field(description="Кейсы пользователя", title="")
    moneys: List[MoneyScheme] = Field(description="Пополнения баланса", title="")
    receiving_skin: List[ReceivingSkinScheme] = Field(description="Выводы скинов", title="")
    referrals: List[UserInfoReferral] = Field(description="id рефералов, которых пригласил пользователь", title="")


class ReceivingScheme(BaseModel):
    id: int = Field(description="id записи", title="")
    user_id: int = Field(description="id пользователя", title="")
    skin_id: int = Field(description="id скина", title="")
    status: str = Field(description="Статус вывода", title="")
    created_at: datetime.datetime = Field(description="Дата", title="")