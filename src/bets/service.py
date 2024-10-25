from typing import List, Optional

from fastapi import HTTPException

from src.bets.models import BetType, Currency
from src.bets.schemas import EventScheme, BetCreateScheme, BetCreateSchemeResponse
from src.unit_of_work import UnitOfWork


class BetService:

    @classmethod
    async def get_active_events(cls, uow: UnitOfWork) -> Optional[List[EventScheme]]:
        async with uow:
            return await uow.event.get_active_events()

    @classmethod
    async def get_event_specific(cls, uow: UnitOfWork, event_id: int) -> EventScheme:
        async with uow:
            result = await uow.event.get_event_specific(event_id)
            if not result:
                raise HTTPException(status_code=404, detail='Событие не найдено')
            return result

    @classmethod
    async def create_bet(cls, uow: UnitOfWork, user_id: int, data: BetCreateScheme) -> BetCreateSchemeResponse:
        async with uow:
            if (data.bet_type == BetType.win and data.bet is False) or (data.bet_type == BetType.winner_first_card and data.bet is False) or (data.bet_type == BetType.winner_second_card and data.bet is False):
                raise HTTPException(status_code=422, detail='Для ставки на события победы, передается только true!')
            if (data.bet_type == BetType.knife and data.event_team_id is not None) or (data.bet_type == BetType.dry_bill and data.event_team_id is not None):
                raise HTTPException(status_code=422, detail='Для ставки на события нож или сухой счёт поле event_team_id должно иметь тип данных null!')
            event = await cls.get_event_specific(uow=uow, event_id=data.event_id)
            if data.event_team_id:
                find_team = False
                for event_team in event.teams:
                    print(event_team.id)
                    if event_team.id == data.event_team_id:
                        find_team = True
                if not find_team:
                    raise HTTPException(status_code=422, detail='Такой команды нет в событии!')
            balance_user = await uow.user.get_balance_user(user_id=user_id, currency=data.currency)
            if balance_user < data.amount:
                raise HTTPException(status_code=400, detail='У вас недостаточно средств!')
            data_dict = data.model_dump()
            data_dict['user_id'] = user_id
            result = await uow.bet.add_and_return_id(data_dict)
            await uow.user.change_balance(user_id=user_id, currency=data.currency, value=-data.amount)
            await uow.commit()
            return BetCreateSchemeResponse(id=result)