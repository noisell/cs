from sqlalchemy import select, update

from src.repository.repository import SQLAlchemyRepository
from src.user.models import User
from src.user.schemas import UserSimpleGet, UserLevelAdminResponse


class UserRepository(SQLAlchemyRepository):
    model = User

    async def get_main_info(self, user_id: int) -> UserSimpleGet | None:
        query = select(self.model).where(self.model.id == user_id)
        query_data = await self.session.execute(query)
        user = query_data.scalar_one_or_none()
        return UserSimpleGet.model_validate(user, from_attributes=True) if user else None

    async def update_username(self, user_id: int, username: str) -> None:
        stmt = update(self.model).values(username=username).where(user_id == self.model.id)
        await self.session.execute(stmt)

    async def update_firstname(self, user_id: int, firstname: str) -> None:
        stmt = update(self.model).values(name=firstname).where(user_id == self.model.id)
        await self.session.execute(stmt)

    async def check_level_admin(self, user_id: int) -> UserLevelAdminResponse:
        query = select(self.model).where(self.model.id == user_id)
        query_data = await self.session.execute(query)
        user = query_data.scalar_one_or_none()
        return UserLevelAdminResponse.model_validate(user, from_attributes=True) if user else None