from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from src.bets.models import Currency
from src.bot.config import ADMIN_URL, bot, SITE_URL

router = Router()

async def create_admin(user_id: int, login: str | int, password: str):
    message = ("👑 <b>Вам выдан доступ к админ панели</b>\n\n"
               f"Ваш логин: <code>{login}</code>\n"
               f"Ваш пароль: <code>{password}</code>\n\n"
               f"Ссылка для входа - {ADMIN_URL}")
    try:
        await bot.send_message(chat_id=user_id, text=message)
        return True
    except Exception as e:
        return f"Ошибка: {e}"


async def bet_message(
        user_id: int,
        win: bool,
        team_one: str,
        team_two: str,
        score_one: int,
        score_two: int,
        price: int | None = None,
        currency: Currency | None = None
) -> None:
    if win:
        message = ("🎉 <b>ВАША СТАВКА ВЫИГРАНА</b>\n\n"
                   f"🎮 {team_one} <b>{score_one} : {score_two}</b> {team_two}\n"
                   f"💸 Сумма выигрыша: <b>{f"${price}" if currency == Currency.usdt else f"{price} coin"}</b>")
    else:
        message = ("🥲 <b>ВАША СТАВКА ПРОИГРАНА</b>\n\n"
                   f"🎮 {team_one} <b>{score_one} : {score_two}</b> {team_two}")
    try:
        await bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="В приложение",
                    web_app=WebAppInfo(url=SITE_URL)
                )]
            ])
        )
    except Exception as e:
        print(e)
        pass


async def clip_message(user_id: int):
    try:
        await bot.send_message(
            chat_id=user_id,
            text="⚡️ Запас обойм восстановлен, скорее заберите ваши монетки!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🎮 Играть",
                    web_app=WebAppInfo(url=SITE_URL)
                )]
            ])
        )
    except Exception as e:
        print(e)
        pass


async def receiving_message(user_id: int, success: bool = True) -> None:
    try:
        await bot.send_message(
            chat_id=user_id,
            text="✅ <b>Вывод скина прошел успешно!</b>" if success else "❗️ <b>Предложение обмена не было принято!</b> Скин возвращен обратно в профиль.",
        )
    except Exception as e:
        print(e)
        pass
