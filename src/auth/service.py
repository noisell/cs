import json
import time
import hmac
import hashlib

from typing import Any
from urllib.parse import unquote
from datetime import datetime, timedelta, timezone
from jwt import ExpiredSignatureError, InvalidTokenError, encode, decode

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from src.auth.config import (
    BOT_TOKEN, PRIVATE_KEY_PASSWORD,
    ACCESS_TOKEN_EXPIRES as ATE,
    REFRESH_TOKEN_EXPIRES as RTE,
    TOKEN_KEY, PRIVATE_KEY_PATH
)
from src.unit_of_work import IUnitOfWork
from src.auth.schemas import Login


def load_private_key(password: str) -> RSAPrivateKey:
    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=password.encode(),
            backend=default_backend()
        )
    return private_key


def encrypt_user_id(user_id, key):
    return Fernet(key).encrypt(user_id.encode()).decode()


def decrypt_user_id(encrypted_user_id, key):
    return Fernet(key).decrypt(encrypted_user_id.encode()).decode()


def encode_jwt(payload: dict[str, int],
               refresh_token: bool = False,
               password: str = PRIVATE_KEY_PASSWORD) -> str:
    private_key = load_private_key(password)
    expire = datetime.now(timezone.utc) + timedelta(seconds=float(RTE) if refresh_token else float(ATE))
    payload.update({"exp": expire.timestamp()})
    encr_user_id = encrypt_user_id(user_id=str(payload.get("user_id")), key=TOKEN_KEY)
    payload.update({"user_id": encr_user_id})
    encoded = encode(payload=payload, key=private_key, algorithm="RS256")
    return encoded


def decode_jwt(token: str | bytes,
               password: str = PRIVATE_KEY_PASSWORD) -> dict[str, int | float]:
    private_key = load_private_key(password)
    public_key = private_key.public_key()
    try:
        decoded = decode(jwt=token, key=public_key, algorithms=["RS256"])
        decr_user_id = int(decrypt_user_id(encrypted_user_id=decoded.get("user_id"), key=TOKEN_KEY))
        decoded.update({"user_id": decr_user_id})
        return decoded
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек!"
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Недопустимый токен"
        )


def check_telegram_auth(user_id: int, init_data: str, max_expire: int | None = 43200) -> dict[str, bool | Any] | bool:
    try:
        secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
        vals: dict[str, Any] = {k: unquote(v) for k, v in [s.split('=', 1) for s in init_data.split('&')]}
        hash_data = vals.pop('hash')
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(vals.items()))
        h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)
        vals_user: dict[str, Any] = json.loads(vals.get('user'))
        return {'hash': h.hexdigest() == hash_data and user_id == vals_user.get('id'),
                'time': int(time.time()) - int(vals.get('auth_date')) <= max_expire}
    except Exception as e:
        print(e)
        return False


# noinspection PyArgumentList
class AuthService:

    @classmethod
    async def check_admin_level(cls, uow: IUnitOfWork, user_id: int) -> int | None:
        async with uow:
            user = await uow.user.check_level_admin(user_id=user_id)
            return user.admin_level if user else None

    @classmethod
    async def get_user_info(cls, uow: IUnitOfWork, user: Login) -> dict | bool:
        async with uow:
            admin_level = await cls.check_admin_level(uow, user.user_id)
            if admin_level is None:
                return False

            await uow.user.update_username(user_id=user.user_id, username=user.username)
            await uow.commit()
            return {'user_id': user.user_id, 'superuser': admin_level}
