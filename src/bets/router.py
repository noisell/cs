from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Body
from starlette.status import HTTP_201_CREATED

from src.bets.schemas import EventScheme, BetCreateScheme, BetCreateSchemeResponse
from src.bets.service import BetService
from src.dependencies import UOWDepends, get_current_user, responses
from src.schemas import TokenPayload

router = APIRouter(
    prefix="/bet",
    tags=["Ставки"]
)


@router.post(path="", name="Создание ставки", status_code=HTTP_201_CREATED, responses=responses(401, 404))
async def create_bet(
        uow: UOWDepends,
        user: Annotated[TokenPayload, Depends(get_current_user)],
        data: BetCreateScheme = Body()
) -> BetCreateSchemeResponse:
    return await BetService().create_bet(uow=uow, user_id=user.user_id, data=data)


@router.get(path="/event", name="Получение активных событий", responses=responses(400, 401, 404))
async def get_events(uow: UOWDepends, _: Annotated[TokenPayload, Depends(get_current_user)]
) -> Optional[List[EventScheme]]:
    return await BetService().get_active_events(uow)


@router.get(path="/event/specific", name="Получение события по id", responses=responses(400, 401, 404))
async def get_event_by_id(uow: UOWDepends, _: Annotated[TokenPayload, Depends(get_current_user)], event_id: int
) -> EventScheme:
    return await BetService().get_event_specific(uow, event_id)