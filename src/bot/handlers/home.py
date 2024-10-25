from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from src.bot.config import SITE_URL

router = Router()

@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
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