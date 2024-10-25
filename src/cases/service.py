import random
from datetime import datetime, UTC, timedelta
from typing import List, Optional

from fastapi import HTTPException

from src.bets.models import Currency
from src.cases.models import TypePriceCase
from src.cases.schemas import CaseAddScheme, CaseGetScheme, SortingCase, CaseAndSkinsScheme, OpenCase, DateOpenCase
from src.unit_of_work import IUnitOfWork


# noinspection PyArgumentList
class CaseService:

    @classmethod
    async def get_all_cases(cls, uow: IUnitOfWork, limit: int, offset: int, sorting: SortingCase) -> Optional[List[CaseGetScheme]]:
        async with uow:
            return await uow.case.get_all_cases(limit=limit, offset=offset, sorting=sorting)

    @classmethod
    async def get_case_by_id(cls, uow: IUnitOfWork, case_id: int) -> Optional[CaseAndSkinsScheme]:
        async with uow:
            return await uow.case.get_case_by_id(case_id)

    @classmethod
    async def check_case_by_id(cls, uow: IUnitOfWork, user_id: int, case_id: int) -> DateOpenCase:
        async with uow:
            date_last_open_case = await uow.user.last_open_case(user_id=user_id)
            if date_last_open_case is None:
                return DateOpenCase(seconds=0)
            case = await cls.get_case_by_id(uow=uow, case_id=case_id)
            if case.type_price == TypePriceCase.usdt:
                return DateOpenCase(seconds=0)
            seconds = ((date_last_open_case + timedelta(days=1)) - datetime.now(UTC).replace(tzinfo=None)).total_seconds()
            return DateOpenCase(seconds=int(seconds) if int(seconds) > 0 else 0)

    @classmethod
    def get_random_skin(cls, skins: dict[int, int]):
        cumulative_chances = []
        total_chance = 0
        for chance in skins.values():
            total_chance += chance
            cumulative_chances.append(total_chance)

        random_value = random.randint(1, total_chance)
        selected_skin = None
        for i, chance in enumerate(cumulative_chances):
            if random_value <= chance:
                selected_skin = list(skins.keys())[i]
                break
        return selected_skin

    @classmethod
    async def open_case(cls, uow: IUnitOfWork, user_id: int, case_id: int) -> OpenCase:
        async with uow:
            case = await uow.case.get_case_by_id(case_id=case_id)
            user_balance = await uow.user.get_balance_user_full(user_id=user_id, currency=case.type_price)
            if user_balance < case.price:
                raise HTTPException(status_code=400, detail='Недостаточно средств!')
            if case.type_price != TypePriceCase.usdt:
                seconds = await cls.check_case_by_id(uow=uow, user_id=user_id, case_id=case_id)
                if seconds.seconds != 0:
                    raise HTTPException(status_code=400, detail='Вы не можете сейчас открыть кейс')
                else:
                    await uow.user.update_last_open_case(user_id=user_id)
            await uow.user.update_balance(user_id=user_id, balance_type=case.type_price, value=-case.price, add=True)
            skins = {skin.id: skin.chance for skin in case.skins}
            case_skin_id = cls.get_random_skin(skins=skins)
            for skin in case.skins:
                if skin.id == case_skin_id:
                    await uow.user_skin.add({"user_id": user_id, "skin_id": skin.skin.id})
                    break
            await uow.user_case.add({"user_id": user_id, "case_skin_id": case_skin_id})
            await uow.commit()
            return OpenCase(id=case_skin_id)
