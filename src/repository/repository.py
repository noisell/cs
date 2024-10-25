from abc import ABC, abstractmethod
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def add_and_return_id(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_and_return_id(self, data: dict) -> int:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        try:
            print(data)
            res = await self.session.execute(stmt)
            return res.scalar_one()
        except IntegrityError:
            return False

    async def add(self, data: dict) -> None:
        stmt = insert(self.model).values(**data)
        try:
            await self.session.execute(stmt)
            return True
        except IntegrityError:
            return False

    async def find_all(self) -> list:
        query = select(self.model)
        res = await self.session.execute(query)
        res = [row[0].to_read_model() for row in res.all()]
        print(f"{res=}")
        return res
