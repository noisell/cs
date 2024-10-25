from abc import ABC, abstractmethod
from typing import Type

from src.database import session_factory
from src.repository.bets import BetRepository, EventRepository, TeamRepository, EventTeamRepository
from src.repository.case import CaseRepository, CaseSkinRepository
from src.repository.skin import SkinRepository, GunRepository
from src.repository.user import UserRepository, UserCaseRepository, UserSkinRepository, UserPromoCodeRepository, \
    UserMoneyRepository, UserReceivingSkinRepository
from src.repository.admin import AdminRepository, PromoCodeRepository, SystemRepository


class IUnitOfWork(ABC):
    user: Type[UserRepository]
    bet: Type[BetRepository]
    event: Type[EventRepository]
    skin: Type[SkinRepository]
    gun: Type[GunRepository]
    case: Type[CaseRepository]
    case_skin: Type[CaseSkinRepository]
    user_case: Type[UserCaseRepository]
    user_skin: Type[UserSkinRepository]
    admin: Type[AdminRepository]
    team: Type[TeamRepository]
    event_team: Type[EventTeamRepository]
    promo_code: Type[PromoCodeRepository]
    user_promo_code: Type[UserPromoCodeRepository]
    user_money: Type[UserMoneyRepository]
    user_receiving: Type[UserReceivingSkinRepository]
    system: Type[SystemRepository]

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork:
    def __init__(self):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.user = UserRepository(self.session)
        self.bet = BetRepository(self.session)
        self.event = EventRepository(self.session)
        self.skin = SkinRepository(self.session)
        self.gun = GunRepository(self.session)
        self.case = CaseRepository(self.session)
        self.case_skin = CaseSkinRepository(self.session)
        self.user_case = UserCaseRepository(self.session)
        self.user_skin = UserSkinRepository(self.session)
        self.admin = AdminRepository(self.session)
        self.team = TeamRepository(self.session)
        self.event_team = EventTeamRepository(self.session)
        self.promo_code = PromoCodeRepository(self.session)
        self.user_promo_code = UserPromoCodeRepository(self.session)
        self.user_money = UserMoneyRepository(self.session)
        self.user_receiving = UserReceivingSkinRepository(self.session)
        self.system = SystemRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
