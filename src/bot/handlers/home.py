from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


from src.bot.config import SITE_URL
from src.unit_of_work import UnitOfWork
from src.user.service import UserService

router = Router()


@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    text = message.text
    if "promo_" in text:
        promo = text.split("promo_")[1]
        uow = UnitOfWork()
        async with uow:
            promo_code = await UserService().activate_promo_code(uow=uow, user_id=message.from_user.id, promo_code=promo)
        return await message.answer(promo_code.message)
    await state.clear()
    await message.answer(
        text="<b>Добро пожаловать в Unlimited Bets CS2!</b>\n\n",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="⚡️ В приложение",
                web_app=WebAppInfo(url=SITE_URL)
            )]
        ])
    )