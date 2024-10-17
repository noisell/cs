from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED

from src.dependencies import UOWDepends, get_current_user, get_current_admin, responses
from src.schemas import TokenPayload
from src.user.schemas import UserSimpleGet, UserAdd, UserUpdateFirstname
from src.user.service import UserService

router = APIRouter(
    prefix="/user",
    tags=["Пользователи"]
)


@router.post(path="", name='Создание пользователя', status_code=HTTP_201_CREATED, responses=responses(400))
async def create(uow: UOWDepends, user: UserAdd = Body()) -> UserSimpleGet:
    return await UserService().user_create(uow=uow, user=user)


@router.get(path="/main", name="Информация о пользователе", responses=responses(400, 401, 404))
async def get_user_info(uow: UOWDepends, user_info: Annotated[TokenPayload, Depends(get_current_user)]
) -> UserSimpleGet:
    user_data = await UserService().user_get_main_info(uow, user_info.user_id)
    return user_data


@router.patch(path="/firstname", name="Обновить имя пользователя", status_code=HTTP_204_NO_CONTENT)
async def update_firstname(
        uow: UOWDepends,
        user_info: Annotated[TokenPayload, Depends(get_current_user)],
        data: UserUpdateFirstname = Body()
) -> None:
    await UserService().update_firstname(uow, user_info.user_id, data.firstname)