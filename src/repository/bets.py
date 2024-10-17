from src.repository.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = None