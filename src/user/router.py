from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED

from src.admin.schemas import InputPromoCodeScheme
from src.dependencies import UOWDepends, get_current_user, responses
from src.schemas import TokenPayload
from src.user.schemas import UserSimpleGet, UserAdd, UserUpdateFirstname, UserAllGet, TradeUrlScheme, AddUSDTScheme, \
    ActivatePromoCode
from src.user.service import UserService

router = APIRouter(
    prefix="/user",
    tags=["Пользователи"]
)


@router.post(path="", name='Создание пользователя', status_code=HTTP_201_CREATED, responses=responses(400))
async def create(uow: UOWDepends, user: UserAdd = Body()) -> UserSimpleGet:
    return await UserService().user_create(uow=uow, user=user)


@router.get(path="/main", name="Информация о пользователе", responses=responses(400, 401, 404))
async def get_user_info(uow: UOWDepends, user_info: Annotated[TokenPayload, Depends(get_current_user)]
) -> UserSimpleGet:
    user_data = await UserService().user_get_main_info(uow, user_info.user_id)
    return user_data


@router.get(path="/check", name="Проверка на существование пользователя", status_code=HTTP_204_NO_CONTENT, responses=responses(404))
async def check_user_exist(uow: UOWDepends, user_id: int) -> None:
    await UserService().user_get_main_info(uow, user_id)

@router.get(path="/full", name="Получение полной информации о пользователе", responses=responses(401))
async def get_full_info_user(
        uow: UOWDepends, user_info: Annotated[TokenPayload, Depends(get_current_user)]) -> UserAllGet:
    return await UserService().get_full_info(uow, user_info.user_id)


@router.patch(path="/firstname", name="Обновить имя пользователя", status_code=HTTP_204_NO_CONTENT)
async def update_firstname(
        uow: UOWDepends,
        user_info: Annotated[TokenPayload, Depends(get_current_user)],
        data: UserUpdateFirstname = Body()
) -> None:
    await UserService().update_firstname(uow, user_info.user_id, data.firstname)


@router.get(path="/tradeURL", name="Получение трейд ссылки", responses=responses(401))
async def get_trade_url(uow: UOWDepends, user: Annotated[TokenPayload, Depends(get_current_user)]) -> TradeUrlScheme:
    return await UserService().get_trade_url(uow, user.user_id)


@router.patch(path="/tradeURL", name="Обновление трейд ссылки", responses=responses(401))
async def update_trade_url(
        uow: UOWDepends, user: Annotated[TokenPayload, Depends(get_current_user)], data: TradeUrlScheme = Body()
) -> None:
    await UserService().update_trade_url(uow=uow, user_id=user.user_id, trade_url=data.trade_url)


@router.patch(path="/clip", name="Забираем обойму", status_code=HTTP_204_NO_CONTENT, responses=responses(401))
async def update_clip(uow: UOWDepends, user: Annotated[TokenPayload, Depends(get_current_user)]) -> None:
    await UserService().update_clip(uow=uow, user_id=user.user_id)


@router.patch(path="/coin", name="Прибавляем монетки", status_code=HTTP_204_NO_CONTENT, responses=responses(401))
async def update_coin(uow: UOWDepends, user: Annotated[TokenPayload, Depends(get_current_user)]) -> None:
    await UserService().update_coin(uow=uow, user_id=user.user_id)


@router.patch(path="/usdt", name="Прибавляем USDT к балансу", status_code=HTTP_204_NO_CONTENT, responses=responses(401))
async def update_usdt(
        uow: UOWDepends, user: Annotated[TokenPayload, Depends(get_current_user)], data: AddUSDTScheme = Body()
) -> None:
    await UserService().update_usdt(uow=uow, user_id=user.user_id, value=data.value)


@router.post(path="/promo/activate", name="Активация промокода", responses=responses(401))
async def promo_activate(
        uow: UOWDepends,
        user: Annotated[TokenPayload, Depends(get_current_user)],
        data: InputPromoCodeScheme = Body()
) -> ActivatePromoCode:
    return await UserService().activate_promo_code(uow=uow, user_id=user.user_id, promo_code=data.name)


@router.get(path="/wallet", name="Получение кошелька", responses=responses(401))
async def get_wallet(uow: UOWDepends, _: Annotated[TokenPayload, Depends(get_current_user)]) -> str:
    return await UserService().get_wallet(uow=uow)