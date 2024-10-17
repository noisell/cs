import pytz
import datetime

from starlette.status import HTTP_400_BAD_REQUEST

from src.user.schemas import UserSimpleGet, UserAdd
from src.unit_of_work import IUnitOfWork
from fastapi import HTTPException


def get_timezone_offset(iana_timezone: str):
    try:
        timezone = pytz.timezone(iana_timezone)
        user_time = datetime.datetime.now(timezone).replace(tzinfo=None)
        utcnow = datetime.datetime.utcnow().replace(tzinfo=None)
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
            print(f"{user_data=}")
            new_user = await uow.user.add(data=user_data)
            if not new_user:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Такой пользователь уже существует!"
                )
            await uow.commit()
        return UserSimpleGet(photo_url=None, count_clip=5, balance_coin=0, balance_usdt=0)

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
