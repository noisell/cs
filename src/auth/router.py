from typing import Annotated, Optional

from cryptography.fernet import InvalidToken
from fastapi import APIRouter, Depends, Body, HTTPException, Response, Cookie
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from src.admin.schemas import SimpleAdminScheme
from src.auth.service import check_telegram_auth, AuthService, encode_jwt, decode_jwt, decrypt_user_id, encrypt_user_id
from src.dependencies import UOWDepends, responses, get_current_user
from src.auth.schemas import Login, AuthResponse, Refresh, LoginAdmin
from src.schemas import TokenPayload
from src.auth.config import REFRESH_TOKEN_EXPIRES as RTE, ADMIN_KEY

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация"],
)


@router.post(path="/login", name="Аутентификация для юзера", status_code=HTTP_204_NO_CONTENT, responses=responses(400, 401, 404))
async def login(response: Response, uow: UOWDepends, data: Login = Body()) -> None:
    # Проверка данных, которые вернулись с Telegram
    result = check_telegram_auth(user_id=data.user_id, init_data=data.init_data)
    if not result or not result.get('hash'):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Некорректные данные! Пожалуйста убедитесь, что пользуетесь официальным клиентом Telegram."
        )
    elif not result.get('time'):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Сессия истекла! Пожалуйста перезапустите приложение."
        )
    else:
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


@router.post(path="/refresh", name="Обновление токена для юзера", status_code=HTTP_204_NO_CONTENT, responses=responses(400, 401))
async def refresh_access_token(
        response: Response,
        uow: UOWDepends,
        refresh: str | None = Cookie(None),
        data: Refresh = Body()

) -> None:
    if not refresh:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Refresh token не найден!"
        )
    decode_refresh = decode_jwt(token=refresh)
    if decode_refresh.get('user_id') == data.user_id:
        superuser = await AuthService().check_user_banned(uow=uow, user_id=data.user_id)
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


@router.post(path="/admin/login", name="Аутентификация для админа", responses=responses(400, 401))
async def admin_login(
        response: Response,
        uow: UOWDepends,
        data: Optional[LoginAdmin] = Body(None),
        remember_me: Optional[str] = Cookie(None)
) -> SimpleAdminScheme:
    if remember_me:
        try:
            user_id = decrypt_user_id(remember_me, ADMIN_KEY)
            admin_data = await AuthService().get_admin_info(uow=uow, user_id=int(user_id))
        except InvalidToken:
            if data:
                admin_data = await AuthService().get_admin_info(uow=uow, data=data)
            else:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Неверные данные о пользователе")
        except ValueError:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Неверные данные о пользователе")
        except Exception as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        if data:
            admin_data = await AuthService().get_admin_info(uow=uow, data=data)
            user_hashed = encrypt_user_id(user_id=data.login, key=ADMIN_KEY)
            if data.remember_me:
                response.set_cookie(
                    key="remember_me",
                    value=user_hashed,
                    max_age=315360000,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                )
        else:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Требуется аутентификация")

    access_token = encode_jwt(payload=admin_data.model_dump())
    refresh_token = encode_jwt(payload={"user_id": admin_data.user_id}, refresh_token=True)
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
    return SimpleAdminScheme(user_id=admin_data.user_id, level=admin_data.level)

@router.post(path="/admin/refresh", name="Обновление токена для админа", responses=responses(400, 401))
async def admin_refresh_access_token(
        response: Response,
        uow: UOWDepends,
        refresh: str | None = Cookie(None),
        data: Refresh = Body()

) -> SimpleAdminScheme:
    if not refresh:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Refresh token не найден!"
        )
    decode_refresh = decode_jwt(token=refresh)
    if decode_refresh.get('user_id') == data.user_id:
        admin = await AuthService().get_admin_info(uow=uow, user_id=data.user_id)
        access_token = encode_jwt(payload={"user_id": admin.user_id, "level": admin.level})
        response.headers['Authorization'] = f"Bearer {access_token}"
        response.headers['Access-Control-Expose-Headers'] = "Authorization"
        return SimpleAdminScheme(user_id=admin.user_id, level=admin.level)
    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Некорректные данные! "
                   "Пожалуйста убедитесь, что токен принадлежит пользователю с указанным user_id"
        )
