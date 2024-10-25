from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, Body
from starlette.status import HTTP_204_NO_CONTENT

from src.dependencies import responses, UOWDepends, get_current_user
from src.schemas import TokenPayload
from src.skins.models import SkinQuality, RaritySkin
from src.skins.schemas import SkinSimpleScheme, Sorting, SearchSkinScheme, GunsScheme, BuySkinScheme, ResSkinScheme, \
    ResSkinResponseScheme
from src.skins.service import SkinService

router = APIRouter(
    prefix="/skin",
    tags=["Скины"]
)


@router.get(path="", name="Получение всех скинов", responses=responses(401))
async def get_user_info(
        uow: UOWDepends,
        _: Annotated[TokenPayload, Depends(get_current_user)],
        limit: int = 25,
        offset: int = 0,
        sorting: Sorting = Sorting.popular,
        name: str | None = None,
        gun_id: int | None = None,
        quality: SkinQuality | None = None,
        rarity: RaritySkin | None = None,
) -> Optional[List[SkinSimpleScheme]]:
    return await SkinService().get_all(
        uow=uow, limit=limit, offset=offset, sorting=sorting, name=name, gun_id=gun_id, quality=quality, rarity=rarity
    )


@router.get(path="/search", name="Поиск скинов")
async def search_skins(name: str) -> Optional[List[SearchSkinScheme]]:
    return await SkinService().search_by_name(name=name)


@router.get(path="/gun", name="Получение всех оружий")
async def gun(uow: UOWDepends) -> List[GunsScheme]:
    return await SkinService().get_all_guns(uow)


@router.post(path="/buy", name="Покупка скина", status_code=HTTP_204_NO_CONTENT, responses=responses(401))
async def buy_skin(uow: UOWDepends, user: Annotated[TokenPayload, Depends(get_current_user)], data: BuySkinScheme = Body()):
    await SkinService().buy_skin(uow=uow, user_id=user.user_id, skin_id=data.id)


@router.get(path="/id", name="Получение скина по id", responses=responses(401))
async def get_skin_by_id(uow: UOWDepends, _: Annotated[TokenPayload, Depends(get_current_user)], skin_id: int) -> SkinSimpleScheme:
    return await SkinService().get_skin_by_id(uow=uow, skin_id=skin_id)


@router.post(path="/receiving", name="Вывод скина", responses=responses(401))
async def receiving(uow: UOWDepends, user: Annotated[TokenPayload, Depends(get_current_user)], data: ResSkinScheme) -> ResSkinResponseScheme:
    return await SkinService().receiving(uow=uow, user_id=user.user_id, skin_id=data.id)


@router.post(path="/sell", name="Продажа скина", status_code=HTTP_204_NO_CONTENT, responses=responses(401))
async def sell_skin(uow: UOWDepends, user: Annotated[TokenPayload, Depends(get_current_user)], data: ResSkinScheme) -> None:
    await SkinService().sell_skin(uow=uow, user_id=user.user_id, skin_id=data.id)