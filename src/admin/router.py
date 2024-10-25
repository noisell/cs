from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Body
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from src.admin.schemas import SimpleAdminScheme, StatusScheme, IdScheme, EventTeamScheme, ChangeScoreScheme, \
    ChangeEvent, CreatePromoCodeScheme, PromoCodeScheme, CaseSkinAddScheme, StatisticsScheme, SimpleTrueAdminScheme, \
    BanScheme, SystemScheme
from src.admin.service import AdminService
from src.bets.schemas import CreateTeam, TeamScheme, EventAddScheme, EventScheme
from src.cases.router import get_all_cases
from src.cases.schemas import CaseAddScheme, SortingCase, CaseAndSkinsScheme, CasesGetAllScheme, CaseSkinChangeScheme
from src.dependencies import UOWDepends, responses, AdminLevelChecker
from src.schemas import AdminPayload
from src.skins.models import SkinQuality, RaritySkin
from src.skins.schemas import GunScheme, Sorting, GunGetScheme, SkinCreateScheme, SkinFullScheme, GunsFullScheme
from src.user.schemas import UserGet, UserFullInfoScheme, ReceivingScheme

router = APIRouter(
    prefix="/admin",
    tags=["Администратор"]
)

@router.post(path="", name="Создание администратора (3)", status_code=HTTP_201_CREATED, responses=responses(400, 401, 403, 404))
async def create_admin(
        uow: UOWDepends,
        #_: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        data: SimpleAdminScheme = Body()
) -> StatusScheme:
    return await AdminService().create_admin(uow=uow, data=data)


@router.post(path="/team", name="Создание команды (1)", status_code=HTTP_201_CREATED, responses=responses(401, 403))
async def create_team(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=1))],
        data: CreateTeam = Body()
) -> IdScheme:
    return await AdminService().create_team(uow=uow, data=data)


@router.get(path="/team", name="Получение всех команд (1)", responses=responses(401, 403))
async def get_all_teams(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=1))],
) -> List[TeamScheme]:
    return await AdminService().get_all_teams(uow=uow)


@router.put(path="/team", name="Изменение данных по команде (1)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def change_team(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=1))],
        data: TeamScheme
) -> None:
    await AdminService().change_team(uow=uow, data=data)


@router.post(path="/event", name="Создание события (1)", status_code=HTTP_201_CREATED, responses=responses(401, 403))
async def create_event(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=1))],
        data: EventAddScheme = Body()
) -> EventTeamScheme:
    return await AdminService().create_event(uow=uow, data=data)


@router.get(path="/event", name="Получение всех событий (1)", responses=responses(401, 403))
async def get_all_events(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=1))],
        limit: int = 30,
        offset: int = 0,
) -> Optional[List[EventScheme]]:
    return await AdminService().get_all_events(uow=uow, limit=limit, offset=offset)


@router.patch(path="/event/team", name="Изменение счета у команды в событии (1)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def change_score_team(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=1))],
        data: ChangeScoreScheme = Body()
) -> None:
    await AdminService().change_score(uow=uow, data=data)


@router.patch(path="/event", name="Изменение события (1)", responses=responses(400, 401, 403))
async def change_event(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=1))],
        data: ChangeEvent = Body()
) -> StatusScheme:
    return await AdminService().close_match(uow=uow, data=data)


@router.post(path="/gun", name="Создание категории оружий (2)", responses=responses(401, 403))
async def create_gun(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=2))],
        data: GunScheme = Body()
) -> IdScheme:
    return await AdminService().create_gun_category(uow=uow, data=data)


@router.get(path="/gun", name="Получение всех оружий (2)", responses=responses(401, 403))
async def get_all_guns(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=2))],
) -> List[GunsFullScheme]:
    return await AdminService().get_all_guns(uow)


@router.put(path="/gun", name="Изменение данных категории оружия (2)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def change_gun(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=2))],
        data: GunGetScheme
) -> None:
    await AdminService().change_gun(uow=uow, data=data)


@router.get(path="/skin", name="Получение всех скинов (2)", responses=responses(401))
async def get_user_info(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=2))],
        limit: int = 25,
        offset: int = 0,
        sorting: Sorting = Sorting.popular,
        name: str | None = None,
        gun_id: int | None = None,
        quality: SkinQuality | None = None,
        rarity: RaritySkin | None = None,
) -> Optional[List[SkinFullScheme]]:
    return await AdminService().get_all_skins(
        uow=uow, limit=limit, offset=offset, sorting=sorting, name=name, gun_id=gun_id, quality=quality, rarity=rarity
    )


@router.post(path="/skin", name="Создание скина (2)", status_code=HTTP_201_CREATED, responses=responses(401, 403))
async def create_skin(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=2))],
        data: SkinCreateScheme = Body()
) -> IdScheme:
    return await AdminService().create_skin(uow=uow, data=data)


@router.put(path="/skin", name="Изменение скина (2)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def change_skin(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=2))],
        data: SkinFullScheme = Body()
) -> None:
    await AdminService().change_skin(uow=uow, data=data)


@router.post(path="/promo", name="Создание промокода (2)", status_code=HTTP_201_CREATED, responses=responses(401, 403))
async def create_promo(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=2))],
        data: CreatePromoCodeScheme = Body()
) -> IdScheme:
    return await AdminService().create_promo(uow=uow, data=data)


@router.get(path="/promo", name="Получение всех промокодов (2)", responses=responses(401, 403))
async def get_promo(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=2))],
) -> List[PromoCodeScheme]:
    return await AdminService().get_all_promo_codes(uow=uow)


@router.put(path="/promo", name="Изменение промокода (2)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def change_promo(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=2))],
        data: PromoCodeScheme = Body()
) -> None:
    await AdminService().change_promo_code(uow=uow, data=data)


@router.post(path="/case", name="Создание кейса (3)", status_code=HTTP_201_CREATED, responses=responses(401, 403))
async def create_case(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        data: CaseAddScheme = Body()
) -> IdScheme:
    return await AdminService().create_case(uow=uow, data=data)


@router.post(path="/case/skin", name="Добавление скина в кейс (3)", status_code=HTTP_201_CREATED, responses=responses(401, 403))
async def create_case_skin(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        data: CaseSkinAddScheme = Body()
) -> IdScheme:
    return await AdminService().create_case_skin(uow=uow, data=data)


@router.put(path="/case", name="Изменение кейса (3)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def change_case(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        data: CasesGetAllScheme = Body()
) -> None:
    await AdminService().change_case(uow=uow, data=data)


@router.patch(path="/case/skin", name="Изменение шанса на выпадение скина в кейсе (3)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def change_case_skin(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        data: CaseSkinChangeScheme = Body()
) -> None:
    await AdminService().change_case_skin(uow=uow, data=data)


@router.get(path="/case", name="Получение всех кейсов (3)", responses=responses(401, 403))
async def get_cases(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        sorting: SortingCase = SortingCase.paid
) -> Optional[List[CaseAndSkinsScheme]]:
   return await AdminService().get_all_cases(uow=uow, sorting=sorting)


@router.delete(path="/case", name="Удаление кейса (3)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def delete_case(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        case_id: int
) -> None:
    await AdminService.delete_case(uow=uow, case_id=case_id)


@router.delete(path="/case/skin", name="Удаление скина из кейса (3)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def delete_case_skin(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        case_skin_id: int
) -> None:
    await AdminService.delete_case_skin(uow=uow, case_skin_id=case_skin_id)


@router.get(path="/statistics", name="Получение статистики системы (3)", responses=responses(401, 403))
async def get_statistics(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
) -> StatisticsScheme:
    return await AdminService().get_statistics(uow=uow)


@router.get(path="/user", name="Получение всех пользователей (3)", responses=responses(401, 403))
async def get_user(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        limit: int = 30,
        offset: int = 0
) -> List[UserGet]:
    return await AdminService().get_all_users(uow=uow, limit=limit, offset=offset)


@router.get(path="/user/id", name="Получение полной инфы о юзере (3)", responses=responses(401, 403, 404))
async def get_user_by_id(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        user_id: int
) -> UserFullInfoScheme:
    return await AdminService().get_user_by_id(uow=uow, user_id=user_id)


@router.get(path="", name="Получение всех админов (3)", responses=responses(401, 403))
async def get_all_admins(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
) -> List[SimpleTrueAdminScheme]:
    return await AdminService().get_all_admins(uow=uow)


@router.post(path="/ban", name="Наложение и снятие бана (3)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def ban(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        data: BanScheme = Body()
) -> None:
    await AdminService().ban_user(uow=uow, user_id=data.user_id, value=data.value)


@router.delete(path="", name="Удаление администратора (3)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def delete_admin(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        user_id: int
) -> None:
    await AdminService().delete_admin(uow=uow, user_id=user_id)


@router.get(path="/system", name="Получение системных данных (3)", responses=responses(401, 403))
async def get_system_data(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
) -> SystemScheme:
    return await AdminService().get_system_data(uow=uow)


@router.put(path="/system", name="Изменение системных данных (3)", status_code=HTTP_204_NO_CONTENT, responses=responses(401, 403))
async def change_system_data(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=3))],
        data: SystemScheme
) -> None:
    await AdminService().change_system_data(uow=uow, data=data)


@router.get(path="/receiving", name="Получение выводов скинов (1)", responses=responses(401, 403))
async def get_receiving(
        uow: UOWDepends,
        _: Annotated[AdminPayload, Depends(AdminLevelChecker(required_level=1))],
) -> List[ReceivingScheme]:
    return await AdminService().get_receiving(uow=uow)