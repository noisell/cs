from typing import List, Optional

from sqlalchemy import select, or_, update, delete
from sqlalchemy.orm import selectinload

from src.admin.schemas import CurrenStatisticsScheme
from src.cases.models import Case, CaseSkin, TypePriceCase
from src.cases.schemas import CaseGetScheme, SortingCase, CaseAndSkinsScheme, CasesGetAllScheme, CaseSkinChangeScheme
from src.repository.repository import SQLAlchemyRepository


class CaseRepository(SQLAlchemyRepository):
    model = Case

    async def get_all_cases(self, limit: int, offset: int, sorting: SortingCase) -> Optional[List[CaseGetScheme]]:
        query = select(self.model).limit(limit).offset(offset)
        if sorting == SortingCase.paid:
            query = query.where(self.model.type_price == TypePriceCase.usdt.value)
        else:
            query = query.where(
                or_(
                    self.model.type_price == TypePriceCase.coin.value,
                    self.model.type_price == TypePriceCase.friend.value
                )
            )
        query_data = await self.session.execute(query)
        cases = query_data.scalars().all()
        return [CaseGetScheme.model_validate(case, from_attributes=True) for case in cases] if cases else None

    async def get_all_cases_full(self, sorting: SortingCase) -> Optional[List[CaseAndSkinsScheme]]:
        query = select(self.model).options(
            selectinload(self.model.skins).selectinload(CaseSkin.skin)
        )
        if sorting == SortingCase.paid:
            query = query.where(self.model.type_price == TypePriceCase.usdt.value)
        else:
            query = query.where(
                or_(
                    self.model.type_price == TypePriceCase.coin.value,
                    self.model.type_price == TypePriceCase.friend.value
                )
            )
        query_data = await self.session.execute(query)
        cases = query_data.scalars().all()
        return [CaseAndSkinsScheme.model_validate(case, from_attributes=True) for case in cases] if cases else None

    async def get_case_by_id(self, case_id: int) -> Optional[CaseAndSkinsScheme]:
        query = select(self.model).where(self.model.id == case_id).options(
            selectinload(self.model.skins).selectinload(CaseSkin.skin)
        )
        query_data = await self.session.execute(query)
        case = query_data.scalar()
        return CaseAndSkinsScheme.model_validate(case, from_attributes=True) if case else None

    async def change_case(self, data: CasesGetAllScheme) -> None:
        stmt = update(self.model).where(self.model.id == data.id).values(
            name=data.name,
            photo_url=data.photo_url,
            type_price=data.type_price,
            price=data.price,
        )
        await self.session.execute(stmt)

    async def delete_case(self, case_id: int) -> None:
        stmt = delete(self.model).where(self.model.id == case_id)
        await self.session.execute(stmt)


class CaseSkinRepository(SQLAlchemyRepository):
    model = CaseSkin

    async def change_chance(self, data: CaseSkinChangeScheme) -> None:
        stmt = update(self.model).where(self.model.id == data.id).values(chance=data.chance)
        await self.session.execute(stmt)

    async def delete_skin(self, case_skin_id: int) -> None:
        stmt = delete(self.model).where(self.model.id == case_skin_id)
        await self.session.execute(stmt)
