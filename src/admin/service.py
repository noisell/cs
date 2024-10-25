from datetime import datetime, UTC, timedelta
from typing import List, Optional

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from src.admin.schemas import SimpleAdminScheme, StatusScheme, IdScheme, EventTeamScheme, ChangeScoreScheme, \
    ChangeEvent, CreatePromoCodeScheme, PromoCodeScheme, CaseSkinAddScheme, StatisticsScheme, SimpleTrueAdminScheme, \
    SystemScheme
from src.auth.service import generate_password
from src.bets.schemas import CreateTeam, TeamScheme, EventAddScheme, EventScheme
from src.cases.schemas import CaseAddScheme, SortingCase, CaseAndSkinsScheme, CasesGetAllScheme, CaseSkinChangeScheme
from src.skins.models import SkinQuality, RaritySkin
from src.skins.schemas import GunScheme, GunGetScheme, SkinCreateScheme, Sorting, SkinFullScheme, GunsFullScheme
from src.tasks.redis_manager import task_manager
from src.tasks.task import schedule_task
from src.unit_of_work import IUnitOfWork
from src.bot.handlers.system import create_admin
from src.user.schemas import UserGet, UserFullInfoScheme, ReceivingScheme


# noinspection PyArgumentList
class AdminService:

    @classmethod
    async def create_admin(cls, uow: IUnitOfWork, data: SimpleAdminScheme) -> StatusScheme:
        async with uow:
            user = await uow.user.get_main_info(user_id=data.user_id)
            if not user:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Пользователь не найден")
            password, salt, hashed_password = generate_password()
            send = await create_admin(user_id=data.user_id, login=data.user_id, password=password)
            if send is not True:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Пользователь заблокировал бота. {send}")
            await uow.admin.add({"id": data.user_id, "level": data.level, "password": hashed_password, "salt": salt})
            await uow.commit()
        return StatusScheme(success=True)

    @classmethod
    async def create_team(cls, uow: IUnitOfWork, data: CreateTeam) -> IdScheme:
        async with uow:
            team_id: int = await uow.team.add_and_return_id(data.model_dump())
            await uow.commit()
        return IdScheme(id=team_id)

    @classmethod
    async def get_all_teams(cls, uow: IUnitOfWork) -> List[TeamScheme]:
        async with uow:
            return await uow.team.get_all()

    @classmethod
    async def change_team(cls, uow: IUnitOfWork, data: TeamScheme) -> None:
        async with uow:
            await uow.team.change_team(data=data)
            await uow.commit()

    @classmethod
    async def create_event(cls, uow: IUnitOfWork, data: EventAddScheme) -> EventTeamScheme:
        async with uow:
            event_id = await uow.event.add_and_return_id({"date_start": data.date_start})
            event_team_one_id = await uow.event_team.add_and_return_id({"event_id": event_id, "team_id": data.team_one_id})
            event_team_two_id = await uow.event_team.add_and_return_id({"event_id": event_id, "team_id": data.team_two_id})
            await uow.commit()
        return EventTeamScheme(event_id=event_id, event_team_one_id=event_team_one_id, event_team_two_id=event_team_two_id)

    @classmethod
    async def get_all_events(cls, uow: IUnitOfWork, limit: int, offset: int) -> Optional[List[EventScheme]]:
        async with uow:
            return await uow.event.get_all_events(limit=limit, offset=offset)

    @classmethod
    async def change_score(cls, uow: IUnitOfWork, data: ChangeScoreScheme) -> None:
        async with uow:
            await uow.event_team.change_score(event_team_id=data.event_team_id, score=data.score)
            await uow.commit()

    @classmethod
    async def close_match(cls, uow: IUnitOfWork, data: ChangeEvent) -> None:
        from src.tasks.bets import pay
        async with uow:
            result = await uow.event.close_match(data=data)
            await uow.commit()
        schedule_task(function=pay, kwargs={"event_id": data.event_id}, task_id=data.event_id)
        return StatusScheme(success=result)

    @classmethod
    async def create_gun_category(cls, uow: IUnitOfWork, data: GunScheme) -> IdScheme:
        async with uow:
            gun_id: int = await uow.gun.add_and_return_id(data.model_dump())
            await uow.commit()
        return IdScheme(id=gun_id)

    @classmethod
    async def get_all_guns(cls, uow: IUnitOfWork) -> List[GunsFullScheme]:
        async with uow:
            return await uow.gun.get_all_guns(parent=True)

    @classmethod
    async def change_gun(cls, uow: IUnitOfWork, data: GunGetScheme) -> None:
        async with uow:
            await uow.gun.change_gun(data=data)
            await uow.commit()

    @classmethod
    async def create_skin(cls, uow: IUnitOfWork, data: SkinCreateScheme) -> IdScheme:
        async with uow:
            skin_id: int = await uow.skin.add_and_return_id(data=data.model_dump())
            await uow.commit()
        task_manager.add_one("skins", skin_id, data.name)
        return IdScheme(id=skin_id)

    @classmethod
    async def get_all_skins(
            cls,
            uow: IUnitOfWork,
            limit: int,
            offset: int,
            sorting: Sorting,
            name: str | None = None,
            gun_id: int | None = None,
            quality: SkinQuality | None = None,
            rarity: RaritySkin | None = None,
    ) -> Optional[List[SkinFullScheme]]:
        async with uow:
            return await uow.skin.get_all_full(
                limit=limit, offset=offset, sorting=sorting, name=name, gun_id=gun_id, quality=quality, rarity=rarity
            )


    @classmethod
    async def change_skin(cls, uow: IUnitOfWork, data: SkinFullScheme) -> None:
        async with uow:
            await uow.skin.change_skin(data=data)
            await uow.commit()

    @classmethod
    async def create_promo(cls, uow: IUnitOfWork, data: CreatePromoCodeScheme) -> IdScheme:
        async with uow:
            promo_id: int = await uow.promo_code.add_and_return_id(data.model_dump())
            await uow.commit()
        return IdScheme(id=promo_id)

    @classmethod
    async def get_all_promo_codes(cls, uow: IUnitOfWork) -> List[PromoCodeScheme]:
        async with uow:
            return await uow.promo_code.get_all()

    @classmethod
    async def change_promo_code(cls, uow: IUnitOfWork, data: PromoCodeScheme) -> None:
        async with uow:
            await uow.promo_code.change_promo_code(data=data)
            await uow.commit()

    @classmethod
    async def create_case(cls, uow: IUnitOfWork, data: CaseAddScheme) -> IdScheme:
        async with uow:
            case_id: int = await uow.case.add_and_return_id(data.model_dump())
            await uow.commit()
        return IdScheme(id=case_id)

    @classmethod
    async def create_case_skin(cls, uow: IUnitOfWork, data: CaseSkinAddScheme) -> IdScheme:
        async with uow:
            case_id: int = await uow.case_skin.add_and_return_id(data.model_dump())
            await uow.commit()
        return IdScheme(id=case_id)

    @classmethod
    async def get_all_cases(cls, uow: IUnitOfWork, sorting: SortingCase) -> Optional[List[CaseAndSkinsScheme]]:
        async with uow:
            return await uow.case.get_all_cases_full(sorting=sorting)

    @classmethod
    async def change_case(cls, uow: IUnitOfWork, data: CasesGetAllScheme) -> None:
        async with uow:
            await uow.case.change_case(data=data)
            await uow.commit()

    @classmethod
    async def change_case_skin(cls, uow: IUnitOfWork, data: CaseSkinChangeScheme) -> None:
        async with uow:
            await uow.case_skin.change_chance(data=data)
            await uow.commit()

    @classmethod
    async def delete_case(cls, uow: IUnitOfWork, case_id: int) -> None:
        async with uow:
            await uow.case.delete_case(case_id=case_id)
            await uow.commit()

    @classmethod
    async def delete_case_skin(cls, uow: IUnitOfWork, case_skin_id: int) -> None:
        async with uow:
            await uow.case_skin.delete_skin(case_skin_id=case_skin_id)
            await uow.commit()

    @classmethod
    async def get_statistics(cls, uow: IUnitOfWork) -> StatisticsScheme:
        date_today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        date_last_day = date_today - timedelta(days=1)
        date_month = date_today - timedelta(days=30)
        date_last_month = date_today - timedelta(days=60)
        async with uow:
            users = await uow.user.statistics(date_today, date_last_day, date_month, date_last_month)
            bets = await uow.bet.statistics(date_today, date_last_day, date_month, date_last_month)
            cases = await uow.user_case.statistics(date_today, date_last_day, date_month, date_last_month)
            skins = await uow.user_skin.statistics(date_today, date_last_day, date_month, date_last_month)
        return StatisticsScheme(users=users, bets=bets, cases=cases, skins=skins)

    @classmethod
    async def get_all_users(cls, uow: IUnitOfWork, limit: int, offset: int) -> List[UserGet]:
        async with uow:
            return await uow.user.get_all_users(limit=limit, offset=offset)

    @classmethod
    async def get_user_by_id(cls, uow: IUnitOfWork, user_id: int) -> UserFullInfoScheme:
        async with uow:
            return await uow.user.get_by_id(user_id=user_id)

    @classmethod
    async def get_all_admins(cls, uow: IUnitOfWork) -> List[SimpleTrueAdminScheme]:
        async with uow:
            return await uow.admin.get_all()

    @classmethod
    async def ban_user(cls, uow: IUnitOfWork, user_id: int, value: bool) -> None:
        async with uow:
            await uow.user.change_banned(user_id=user_id, value=value)
            await uow.commit()

    @classmethod
    async def delete_admin(cls, uow: IUnitOfWork, user_id: int) -> None:
        async with uow:
            await uow.admin.delete_admin(user_id=user_id)
            await uow.commit()

    @classmethod
    async def get_system_data(cls, uow: IUnitOfWork) -> SystemScheme:
        async with uow:
            market = await uow.system.get_data(name="market")
            ton = await uow.system.get_data(name="ton")
            return SystemScheme(market=market, ton=ton)

    @classmethod
    async def change_system_data(cls, uow: IUnitOfWork, data: SystemScheme) -> None:
        async with uow:
            await uow.system.change_data(name="market", value=data.market)
            await uow.system.change_data(name="ton", value=data.ton)
            await uow.commit()

    @classmethod
    async def get_receiving(cls, uow: IUnitOfWork) -> List[ReceivingScheme]:
        async with uow:
            return await uow.user_receiving.get_all()
