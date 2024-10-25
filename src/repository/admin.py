from typing import Optional, List, Union

from sqlalchemy import select, update, delete

from src.admin.models import Admin, PromoCode, System
from src.admin.schemas import AdminScheme, PromoCodeScheme, SimpleAdminScheme, SimpleTrueAdminScheme, SystemScheme
from src.repository.repository import SQLAlchemyRepository


class AdminRepository(SQLAlchemyRepository):
    model = Admin

    async def get_info(self, user_id: int) -> Optional[AdminScheme]:
        query = select(self.model).where(self.model.id == user_id)
        query_data = await self.session.execute(query)
        admin = query_data.scalar()
        return AdminScheme.model_validate(admin, from_attributes=True) if admin else None

    async def get_all(self) -> List[SimpleTrueAdminScheme]:
        query = select(self.model)
        query_data = await self.session.execute(query)
        admins = query_data.scalars().all()
        return [SimpleTrueAdminScheme.model_validate(admin, from_attributes=True) for admin in admins]

    async def delete_admin(self, user_id: int) -> None:
        stmt = delete(self.model).where(self.model.id == user_id)
        await self.session.execute(stmt)


class PromoCodeRepository(SQLAlchemyRepository):
    model = PromoCode

    async def get_all(self) -> List[PromoCodeScheme]:
        query = select(self.model).order_by(self.model.count.desc())
        query_data = await self.session.execute(query)
        promo_codes = query_data.scalars().all()
        return [PromoCodeScheme.model_validate(promo_code, from_attributes=True) for promo_code in promo_codes]

    async def check_promo_code(self, promo_code: str) -> Union[PromoCodeScheme, bool]:
        query = select(self.model).where(self.model.name == promo_code)
        query_data = await self.session.execute(query)
        promo_code = query_data.scalar()
        if not promo_code or promo_code.count <= 0:
            return False
        return PromoCodeScheme.model_validate(promo_code, from_attributes=True)

    async def update_promo_code(self, promo_code_id: int) -> None:
        stmt = update(self.model).where(self.model.id == promo_code_id).values(count=self.model.count - 1)
        await self.session.execute(stmt)

    async def change_promo_code(self, data: PromoCodeScheme) -> None:
        stmt = update(self.model).where(self.model.id == data.id).values(
            name=data.name,
            type=data.type,
            value=data.value,
            count=data.count
        )
        await self.session.execute(stmt)


class SystemRepository(SQLAlchemyRepository):
    model = System

    async def get_data(self, name: str) -> str:
        query = select(self.model.value).where(self.model.name == name)
        query_data = await self.session.execute(query)
        result = query_data.scalar_one_or_none()
        return result

    async def change_data(self, name: str, value: str) -> None:
        stmt = update(self.model).where(self.model.name == name).values(value=value)
        await self.session.execute(stmt)
