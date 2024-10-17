from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, Response, Cookie
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from src.auth.service import check_telegram_auth, AuthService, encode_jwt, decode_jwt
from src.dependencies import UOWDepends, responses, get_current_user
from src.auth.schemas import Login, AuthResponse, Refresh
from src.schemas import TokenPayload
from src.auth.config import REFRESH_TOKEN_EXPIRES as RTE

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация"],
)


@router.post(path="/login", responses=responses(400, 401, 404), status_code=HTTP_204_NO_CONTENT)
async def login(response: Response, uow: UOWDepends, data: Login = Body()) -> None:
    # Проверка данных, которые вернулись с Telegram
    # result = check_telegram_auth(user_id=data.user_id, init_data=data.init_data)
    # if not result or not result.get('hash'):
    #     raise HTTPException(
    #         status_code=HTTP_400_BAD_REQUEST,
    #         detail="Некорректные данные! Пожалуйста убедитесь, что пользуетесь официальным клиентом Telegram."
    #     )
    # elif not result.get('time'):
    #     raise HTTPException(
    #         status_code=HTTP_401_UNAUTHORIZED,
    #         detail="Сессия истекла! Пожалуйста перезапустите приложение."
    #     )
    # else:
        # Получение информации о пользователе
        user_data = await AuthService().get_user_info(uow, data)
        if not user_data:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Пользователь не найден!"
            )
        # Выпуск токенов
        access_token = encode_jwt(payload=user_data)
        refresh_token = encode_jwt(payload={"user_id": data.user_id}, refresh_token=True)

        response.set_cookie(
            key="refresh",
            value=refresh_token,
            max_age=RTE,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        response.headers['Authorization'] = f"Bearer {access_token}"
        response.headers['Access-Control-Expose-Headers'] = "Authorization"


@router.post(path="/refresh", responses=responses(400, 401))
async def refresh_access_token(
        response: Response,
        uow: UOWDepends,
        refresh: str | None = Cookie(None),
        data: Refresh = Body()

) -> AuthResponse:
    if not refresh:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Refresh token не найден!"
        )
    decode_refresh = decode_jwt(token=refresh)
    if decode_refresh.get('user_id') == data.user_id:
        superuser = await AuthService().check_admin_level(uow=uow, user_id=data.user_id)
        access_token = encode_jwt(payload={"user_id": data.user_id, "superuser": superuser})
        response.headers['Authorization'] = f"Bearer {access_token}"
        response.headers['Access-Control-Expose-Headers'] = "Authorization"
        return AuthResponse.model_validate({'result': True})
    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Некорректные данные! "
                   "Пожалуйста убедитесь, что токен принадлежит пользователю с указанным user_id"
        )


@router.post(path="/validateJWTToken", status_code=HTTP_204_NO_CONTENT)
async def validate_jwt_token(_: Annotated[TokenPayload, Depends(get_current_user)]) -> None:
    return

