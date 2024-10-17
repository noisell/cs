from pydantic import BaseModel, Field


class Error(BaseModel):
    code: int = Field(description="Код ошибки.\n\n"
                                  "401 - Устаревшие данные в поле auth_date из Telegram\n\n"
                                  "403 - Данные из поля Telegram.WebApp.initData не прошли проверку",
                      title="")
    message: str = Field(description="Текст ошибки. Выводится в заголовок popup", title="")
    description: str = Field(description="Описание ошибки. Выводится в описание к popup", title="")


class Login(BaseModel):
    init_data: str = Field(description="Строка с необработанными данными из window.Telegram.WebApp.initData", title="")
    user_id: int = Field(description="ID пользователя в Telegram", examples=["78273823"], title="")
    username: str | None = Field(None, description="Username пользователя в Telegram", examples=["mirry_manager"], title="")


class Refresh(BaseModel):
    user_id: int = Field(description="ID пользователя в Telegram", examples=["23632423"], title="")


class LoginResponse(BaseModel):
    access_token: str = Field(description="Access Token. Срок действия 10 минут", title="")
    refresh_token: str = Field(description="Refresh Token. Срок действия 12 часов", title="")


class AuthResponse(BaseModel):
    result: bool = Field(True,
                         description="Успешно? Возвращается только true, в случаи ошибки будет вызвано исключение",
                         title="")


class ValidateJWTTokenResponse(BaseModel):
    valid: bool = Field(description="Валидный токен или нет", title="")
