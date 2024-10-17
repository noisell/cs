from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jwt import PyJWTError, ExpiredSignatureError, InvalidTokenError, DecodeError, InvalidSignatureError
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from fastapi.security.utils import get_authorization_scheme_param

from src.auth.service import decode_jwt
from src.schemas import TokenPayload, get_error_responses
from src.unit_of_work import IUnitOfWork, UnitOfWork

UOWDepends = Annotated[IUnitOfWork, Depends(UnitOfWork)]
oauth2_scheme = APIKeyHeader(name="Authorization", scheme_name="JWTUserID", auto_error=False)



def responses(*errors: int):
    all_responses = get_error_responses()
    return {error: all_responses[error] for error in errors}


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenPayload:
    if token is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Отсутствует токен!")
    try:
        scheme, value = get_authorization_scheme_param(token)
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Неправильная схема аутентификации. Требуется Bearer."
            )
        if not value:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Отсутствует токен!")
        payload = decode_jwt(value)
        if payload.get("user_id") is None or payload.get("superuser") is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Некорректные данные!")
        token_data = TokenPayload(**payload)
    except ExpiredSignatureError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Срок действия токена истек!")
    except InvalidSignatureError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Недопустимый токен: неправильная подпись")
    except DecodeError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Недопустимый токен: ошибка декодирования")
    except InvalidTokenError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Недопустимый токен: ошибка неизвестна")
    except PyJWTError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Отказано в доступе!")
    return token_data


def get_current_admin(user: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
    if not user.superuser:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Доступ запрещен! Требуются права администратора."
        )
    return user
