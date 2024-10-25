import pytz
import datetime

from starlette.status import HTTP_400_BAD_REQUEST

from src.admin.models import PromoType
from src.cases.models import TypePriceCase
from src.user.schemas import UserSimpleGet, UserAdd, UserAllGet, TradeUrlScheme, ActivatePromoCode
from src.unit_of_work import IUnitOfWork
from fastapi import HTTPException


def get_timezone_offset(iana_timezone: str):
    try:
        timezone = pytz.timezone(iana_timezone)
        user_time = datetime.datetime.now(timezone).replace(tzinfo=None, second=0, microsecond=0)
        utcnow = datetime.datetime.now(datetime.UTC).replace(tzinfo=None, second=0, microsecond=0)
        offset = int((user_time - utcnow).total_seconds()) / 60
        return int(offset)
    except Exception as e:
        print(e)
        return 180


# noinspection PyArgumentList
class UserService:

    @classmethod
    async def user_create(cls, uow: IUnitOfWork, user: UserAdd) -> UserSimpleGet:
        user_data = user.model_dump()
        time_zone = user_data.get('time_zone')
        time_zone_offset = get_timezone_offset(time_zone) if time_zone else 180
        user_data['time_zone'] = time_zone_offset
        async with uow:
            if user.referrer_id:
                user_data['use_ref_bonus'] = False
                await cls.update_balance(uow=uow, user_id=user.id, balance_type=TypePriceCase.friend, value=1, add=True)
                # Можно отправить сообщение о новом юзере
            new_user = await uow.user.add(data=user_data)
            if not new_user:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Такой пользователь уже существует!"
                )
            await uow.commit()
        return UserSimpleGet(photo_url=None, count_clip=5, balance_coin=0, balance_usdt=0, balance_referrers=0)

    @classmethod
    async def update_balance(
            cls, uow: IUnitOfWork, user_id: int, balance_type: TypePriceCase, value: float | int, add: bool = False
    ) -> None:
        async with uow:
            await uow.user.update_balance(user_id=user_id, balance_type=balance_type, value=value, add=add)
            await uow.commit()

    @classmethod
    async def user_get_main_info(cls, uow: IUnitOfWork, user_id: int) -> UserSimpleGet:
        async with uow:
            result = await uow.user.get_main_info(user_id=user_id)
            if not result:
                raise HTTPException(status_code=404, detail='Пользователь не найден')
            return result

    @classmethod
    async def update_firstname(cls, uow: IUnitOfWork, user_id: int, firstname: str) -> None:
        async with uow:
            await uow.user.update_firstname(user_id=user_id, firstname=firstname)


    @classmethod
    async def get_full_info(cls, uow: IUnitOfWork, user_id: int) -> UserAllGet:
        async with uow:
            return await uow.user.get_full_info(user_id=user_id)


    @classmethod
    async def get_trade_url(cls, uow: IUnitOfWork, user_id: int) -> TradeUrlScheme:
        async with uow:
            result = await uow.user.get_trade_url(user_id=user_id)
            return TradeUrlScheme(trade_url=result)

    @classmethod
    async def update_trade_url(cls, uow: IUnitOfWork, user_id: int, trade_url: str) -> None:
        async with uow:
            await uow.user.update_trade_url(user_id=user_id, trade_url=trade_url)
            await uow.commit()

    @classmethod
    async def update_clip(cls, uow: IUnitOfWork, user_id: int) -> None:
        from src.tasks.task import schedule_task
        from src.tasks.update_clips import update_clip
        async with uow:
            await uow.user.update_clip(user_id=user_id)
            await uow.commit()
        schedule_task(function=update_clip, kwargs={'user_id': user_id}, task_id=user_id, delay=3600)

    @classmethod
    async def update_coin(cls, uow: IUnitOfWork, user_id: int) -> None:
        async with uow:
            await uow.user.update_balance(user_id=user_id, balance_type=TypePriceCase.coin, value=1, add=True)
            await uow.commit()

    @classmethod
    async def update_usdt(cls, uow: IUnitOfWork, user_id: int, value: int) -> None:
        async with uow:
            await uow.user.update_balance(user_id=user_id, balance_type=TypePriceCase.usdt, value=value, add=True)
            await uow.user_money.add({"user_id": user_id, "amount": value})
            await uow.commit()

    @classmethod
    async def activate_promo_code(cls, uow: IUnitOfWork, user_id: int, promo_code: str) -> ActivatePromoCode:
        async with uow:
            check_promo_code = await uow.promo_code.check_promo_code(promo_code=promo_code)
            if check_promo_code is False:
                return ActivatePromoCode(activated=False, message="Промокод не найден или истек!")
            check_user_used_promo_code = await uow.user_promo_code.check_used(user_id=user_id, promo_code_id=check_promo_code.id)
            if check_user_used_promo_code is False:
                return ActivatePromoCode(activated=False, message="Вы уже использовали этот промокод!")
            await uow.user_promo_code.add({"user_id": user_id, "promo_code_id": check_promo_code.id})
            await uow.promo_code.update_promo_code(promo_code_id=check_promo_code.id)
            if check_promo_code.type == PromoType.usdt:
                await uow.user.update_balance(user_id=user_id, balance_type=TypePriceCase.usdt,  value=check_promo_code.value, add=True)
            elif check_promo_code.type == PromoType.coin:
                await uow.user.update_balance(user_id=user_id, balance_type=TypePriceCase.coin, value=check_promo_code.value, add=True)
            else:
                await uow.user.update_clip(user_id=user_id, minus=False, value=check_promo_code.value)
            await uow.commit()
        return ActivatePromoCode(activated=True, message="Промокод успешно активирован!")

    @classmethod
    async def get_wallet(cls, uow: IUnitOfWork) -> str:
        async with uow:
            return await uow.system.get_data(name="ton")