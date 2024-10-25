from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Body
from starlette.status import HTTP_204_NO_CONTENT

from src.cases.schemas import CaseAddScheme, CaseGetScheme, SortingCase, CaseAndSkinsScheme, OpenCase, DateOpenCase
from src.cases.service import CaseService
from src.dependencies import responses, UOWDepends, get_current_user
from src.schemas import TokenPayload

router = APIRouter(
    prefix="/case",
    tags=["Кейсы"]
)

@router.get(path="", name="Получение всех кейсов", responses=responses(401))
async def get_all_cases(
        uow: UOWDepends,
        _: Annotated[TokenPayload, Depends(get_current_user)],
        limit: int = 25,
        offset: int = 0,
        sorting: SortingCase = SortingCase.paid
) -> Optional[List[CaseGetScheme]]:
    return await CaseService().get_all_cases(uow=uow, limit=limit, offset=offset, sorting=sorting)


@router.get(path="/id", name="Получения кейса по id", responses=responses(401))
async def get_case_by_id(uow: UOWDepends, _: Annotated[TokenPayload, Depends(get_current_user)], case_id: int) -> Optional[CaseAndSkinsScheme]:
    return await CaseService().get_case_by_id(uow=uow, case_id=case_id)


@router.get(path="/check", name="Проверка кейса", responses=responses(401))
async def check_case_by_id(uow: UOWDepends, user: Annotated[TokenPayload, Depends(get_current_user)], case_id: int) -> DateOpenCase:
    return await CaseService().check_case_by_id(uow=uow, user_id=user.user_id, case_id=case_id)


@router.post(path="/open", name="Открытие кейса", responses=responses(401, 400))
async def open_case(
        uow: UOWDepends, user: Annotated[TokenPayload, Depends(get_current_user)], data: OpenCase = Body()
) -> OpenCase:
    return await CaseService().open_case(uow=uow, user_id=user.user_id, case_id=data.id)
